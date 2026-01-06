from datetime import datetime

from sqlalchemy import Integer, String, DateTime, SmallInteger, ForeignKey, func, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

class Events(Base):
    __tablename__ = 'Events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    exp_gained: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    special: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Levels(Base):
    __tablename__ = 'Levels'

    level: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    lvlup_exp: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_event: Mapped[int | None] = mapped_column(ForeignKey(Events.id), nullable=True)


class Players(Base):
    __tablename__ = 'Players'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(ForeignKey(Levels.level), default=1)
    exp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class PlayerEvents(Base):
    __tablename__ = 'PlayerEvents'

    player: Mapped[int] = mapped_column(ForeignKey(Players.id), primary_key=True)
    event: Mapped[int] = mapped_column(ForeignKey(Events.id), primary_key=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_default=func.now(), onupdate=func.now())
    repeats: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
