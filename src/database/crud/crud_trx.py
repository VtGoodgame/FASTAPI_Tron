from sqlalchemy.orm import Session
from src.database.models.db_models import TRC20Transaction
from src.Schemas.API_schema import TransactionItem, ms_to_datetime


async def save_transaction(db: Session, trx: TransactionItem):
    db_trx = TRC20Transaction(
        transaction_id=trx.transaction_id,
        token_symbol=trx.token_info.symbol,
        token_address=trx.token_info.address,
        token_name=trx.token_info.name,
        token_decimals=trx.token_info.decimals,
        block_timestamp=ms_to_datetime(trx.block_timestamp),
        from_address=trx.from_,  
        to_address=trx.to,
        trx_type=trx.type,
        value=trx.value
    )
    db.add(db_trx)
    db.commit()
    db.refresh(db_trx)
    return db_trx


async def get_transactions_by_address(db: Session, address: str):
    return db.query(TRC20Transaction)\
             .filter(TRC20Transaction.to_address == address)\
             .all()


async def get_last_100_transactions(db: Session):
    return db.query(TRC20Transaction)\
             .order_by(TRC20Transaction.block_timestamp.desc())\
             .limit(100)\
             .all()
