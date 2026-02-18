from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    ticker = Column(String, index=True)
    money_investment = Column(Float)
    init_price = Column(Float)
    shares = Column(Float)
    is_open = Column(Boolean, default=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    close_price = Column(Float, nullable=True)

class Session(Base):
    __tablename__ = "sessions"
    token = Column(String, primary_key=True)
    username = Column(String, index=True)
