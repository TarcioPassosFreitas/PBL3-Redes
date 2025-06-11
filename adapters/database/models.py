from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserORM(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), nullable=True)
    name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    active_sessions = Column(JSON, default=list)
    total_charges = Column(Numeric(precision=18, scale=8), default=0)
    total_sessions = Column(Integer, default=0)
    active_reservations = Column(JSON, default=list)

class StationORM(Base):
    __tablename__ = 'stations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False)
    power_output = Column(Numeric(precision=18, scale=8), nullable=False)
    price_per_hour = Column(Numeric(precision=18, scale=8), nullable=False)
    is_available = Column(Boolean, default=True)
    current_session_id = Column(Integer, nullable=True)
    reservations = Column(JSON, default=dict)
    total_sessions = Column(Integer, default=0)
    total_revenue = Column(Numeric(precision=18, scale=8), default=0) 