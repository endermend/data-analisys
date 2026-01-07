import logging
import os
import sys
import time
from random import randint, choices

from sqlalchemy import create_engine, and_
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from . import *

# Введение констант
EVENT_WEIGHTS = [0.05, 0.02, 0.93]
DB_RETRY_ATTEMPTS = 10
DB_RETRY_DELAY = 5
APP_START_DELAY = 10

# Глобальные счетчики
events_cnt = 0
players_cnt = 0

# Установка логера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def get_engine():
    """Создает и возвращает движок базы данных. Включает в себя логину попыток"""
    connection_string = os.getenv('DB_URL')
    
    for attempt in range(DB_RETRY_ATTEMPTS):
        try:
            return create_engine(connection_string)
        except OperationalError:
            if attempt < DB_RETRY_ATTEMPTS - 1:
                time.sleep(DB_RETRY_DELAY)
    
    sys.exit(1)


def initialize_database():
    """Инициализация базы данных"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    return SessionFactory()


def add_levels(session):
    """Создание уровней"""
    if session.query(func.count(Levels.level)).scalar() > 0:
        return
    
    # Добавление специального события по достижению юбилейных уровней
    event = Events(
        name='Its yours anniversary!',
        exp_gained=1000,
        special=True
    )
    session.add(event)
    session.commit()
    
    logger.info(f'special_event: {event.id}')
    
    # Создание уровней 1-20
    exp_level = lambda i: int((100 + 383 * (i - 1)) * (2 ** ((i - 1) / 5)))
    
    for i in range(1, 21):
        assigned_event = None if i % 10 != 0 else event.id
        level = Levels(
            level=i,
            lvlup_exp=exp_level(i),
            assigned_event=assigned_event
        )
        session.add(level)


def add_player(session):
    """Добавление нового игрока в базу данных"""
    global players_cnt
    next_nick = generate_nick('en')
    player = Players(name=next_nick)
    session.add(player)
    players_cnt += 1


def add_event(session):
    """Добавление нового события в базу данных"""
    global events_cnt
    next_event = generate_event()
    event = Events(
        name=next_event,
        exp_gained=randint(0, 1000)
    )
    session.add(event)
    events_cnt += 1


def get_random_event(session):
    """Получение случайного обычного события"""
    global events_cnt
    
    for _ in range(events_cnt):
        event_id = randint(1, events_cnt)
        event = session.query(Events).filter_by(id=event_id).first()
        
        if event is not None and not event.special:
            return event
    
    return None


def update_player_event(session, player_id, event_id):
    """Обновление или создание отношения игрок-событие"""
    player_event = session.query(PlayerEvents).where(
        and_(
            PlayerEvents.player == player_id,
            PlayerEvents.event == event_id
        )
    ).first()
    
    if player_event is None:
        player_event = PlayerEvents(
            player=player_id,
            event=event_id
        )
        session.add(player_event)
    else:
        player_event.repeats += 1


def add_player_event(session):
    """Создание отношения игрок-событие с обновлением опыта"""
    global events_cnt, players_cnt
    
    if events_cnt == 0 or players_cnt == 0:
        return
    
    player_id = randint(1, players_cnt)
    player = session.query(Players).filter_by(id=player_id).first()
    event = get_random_event(session)
    
    if event is None:
        return
    
    # Обновление отношения игрок-событие
    update_player_event(session, player_id, event.id)
    
    # Обновление опыта
    exp_gained = event.exp_gained + player.exp
    player.exp = 0
    
    while exp_gained > 0:
        current_level = session.query(Levels).filter_by(
            level=player.level
        ).first()
        next_level = session.query(Levels).filter_by(
            level=player.level + 1
        ).first()
        
        if exp_gained < current_level.lvlup_exp or next_level is None:
            player.exp = exp_gained
            break
        
        exp_gained -= current_level.lvlup_exp
        player.level += 1
        
        if next_level.assigned_event is None:
            continue
        
        event_id = next_level.assigned_event
        assigned_event = session.query(Events.exp_gained).filter_by(
            id=event_id
        ).first()
        
        update_player_event(session, player_id, event_id)
        exp_gained += assigned_event.exp_gained


def run_event_loop(session):
    """Основной цикл программы"""
    global events_cnt, players_cnt
    
    # Инициализация
    add_levels(session)
    players_cnt = session.query(func.count(Players.id)).scalar()
    events_cnt = session.query(func.count(Events.id)).scalar()
    
    # Доступные события
    events = [add_event, add_player, add_player_event]
    
    # Основной цикл
    while True:
        chosen_event = choices(events, EVENT_WEIGHTS)[0]
        chosen_event(session)
        session.commit()


def main():
    """Точка запуска программы"""
    time.sleep(APP_START_DELAY)
    session = initialize_database()
    run_event_loop(session)


if __name__ == "__main__":
    main()