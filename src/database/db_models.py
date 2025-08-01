from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from src.database.database import Base  

class AccountResource(Base):
    __tablename__ = "account_resources"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(100), unique=True, index=True, nullable=False)

    # Пропускная способность
    free_net_used = Column(Integer, default=0)
    free_net_limit = Column(Integer, default=0)
    net_used = Column(Integer, default=0)
    net_limit = Column(Integer, default=0)
    total_net_limit = Column(Integer, default=0)
    total_net_weight = Column(Integer, default=0)

    # Энергия
    energy_used = Column(Integer, default=0)
    energy_limit = Column(Integer, default=0)
    total_energy_limit = Column(Integer, default=0)
    total_energy_weight = Column(Integer, default=0)

    # Голосование
    tron_power_limit = Column(Integer, default=0)
    tron_power_used = Column(Integer, default=0)

    # TRC10 активы
    asset_net_used = Column(JSON, default=dict)
    asset_net_limit = Column(JSON, default=dict)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)