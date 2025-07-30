from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TRC20Transaction(Base):
    __tablename__ = "trc20_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    token_symbol = Column(String)
    token_address = Column(String)
    token_name = Column(String)
    token_decimals = Column(Integer)
    block_timestamp = Column(DateTime)
    from_address = Column(String)
    to_address = Column(String)
    trx_type = Column(String)
    value = Column(String)
