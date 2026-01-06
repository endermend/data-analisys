import os, time
from random import randint, choices

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from . import generate_nick, generate_event
from . import *

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

events_cnt = 0
players_cnt = 0


def get_engine():
    connection_string = os.getenv('DB_URL')
    for tries in range(10):
        try:
            engine = create_engine(connection_string)
            return engine
        except OperationalError  as e:
            time.sleep(5)
    exit(1)

def add_player(session):
    global players_cnt
    next_nick = generate_nick('en')
    player = Players(name=next_nick)
    session.add(player)
    players_cnt += 1


def add_event(session):
    global events_cnt
    next_event = generate_event()
    event = Events(name=next_event, exp_gained=randint(0, 1000))
    session.add(event)
    events_cnt += 1


def update_player_event(session, player_id, event_id):
    player_event = session.query(PlayerEvents).where(and_(PlayerEvents.player == player_id,
                                                      PlayerEvents.event == event_id)).first()
    if player_event is None:
        player_event = PlayerEvents(player=player_id, event=event_id)
        session.add(player_event)
    else:
        player_event.repeats += 1

def get_random_event():
    global events_cnt
    for i in range(events_cnt):  
        event_id = randint(1, events_cnt)
        event = session.query(Events).filter_by(id = event_id).first()
        if event is not None and not event.special:
            return event

def add_player_event(session):
    global events_cnt
    global players_cnt
    if events_cnt == 0 or players_cnt == 0:
        return
    player_id = randint(1, players_cnt)
    player = session.query(Players).filter_by(id = player_id).first()
    event = get_random_event()
    if event is None:
        return
    update_player_event(session, player_id, event.id)
    exp_gained = event.exp_gained + player.exp
    player.exp = 0
    while exp_gained > 0:
        level = session.query(Levels).filter_by(level = player.level).first()
        next_level = session.query(Levels).filter_by(level = player.level + 1).first()
        if exp_gained < level.lvlup_exp or next_level is None:
            player.exp = exp_gained
            break
        exp_gained -= level.lvlup_exp
        player.level += 1
        if event_id := next_level.assigned_event is None:
            continue
        event = session.query(Events.exp_gained).filter_by(id = event_id).first()
        update_player_event(session, player_id, event_id)
        exp_gained += event

def add_levels(session):
    if session.query(func.count(Levels.level)).scalar() > 0:
        return
    event = Events(name='Its yours anniversary!', exp_gained=1000, special=True)
    session.add(event)
    session.commit()
    exp_level = lambda i: int((100+383*(i-1))*(2**((i-1)/3)))
    logger.info(f'special_event: {event.id}')
    for i in range(1, 21):
        assigned_event = None if i % 10 != 0 else event.id
        level = Levels(level=i, lvlup_exp=exp_level(i), assigned_event=assigned_event)
        session.add(level)

def loop(session):
    global events_cnt
    global players_cnt
    add_levels(session)
    players_cnt = session.query(func.count(Players.id)).scalar()
    events_cnt = session.query(func.count(Events.id)).scalar()
    events = [add_event, add_player, add_player_event]
    while True:
        choices(events, [0.2, 0.1, 0.7])[0](session)
        session.commit()


if __name__ == "__main__":
    time.sleep(10)
    engine = get_engine()
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    loop(session)
