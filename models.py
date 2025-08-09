# models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    balance = Column(Integer, default=0)
    banned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TopUp(Base):
    __tablename__ = "topups"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String)

class GameLog(Base):
    __tablename__ = "gamelogs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    game = Column(String)
    stake = Column(Integer)
    result = Column(String)
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True)
    game = Column(String)
    stake = Column(Integer)
    creator_tg = Column(Integer)
    opponent_tg = Column(Integer, nullable=True)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)