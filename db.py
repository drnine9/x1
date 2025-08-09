# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, TopUp, Setting, GameLog, Challenge
from config import DATABASE_URL, DEFAULT_WIN_RATES
import logging

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # initialize settings if missing
    db = SessionLocal()
    for k,v in DEFAULT_WIN_RATES.items():
        if not db.query(Setting).filter_by(key=f"win_rate:{k}").first():
            db.add(Setting(key=f"win_rate:{k}", value=str(v)))
    if not db.query(Setting).filter_by(key="global_win_rate").first():
        db.add(Setting(key="global_win_rate", value="1.0"))  # global multiplier
    db.commit()
    db.close()

# helpers
def get_setting(key, default=None):
    db = SessionLocal()
    s = db.query(Setting).filter_by(key=key).first()
    db.close()
    return s.value if s else default

def set_setting(key, value):
    db = SessionLocal()
    s = db.query(Setting).filter_by(key=key).first()
    if not s:
        s = Setting(key=key, value=str(value))
        db.add(s)
    else:
        s.value = str(value)
    db.commit()
    db.close()