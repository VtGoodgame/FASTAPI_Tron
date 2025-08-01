# src/database/crud/crud_account.py
import datetime 
from sqlalchemy.orm import Session
from FASTAPI_Tron.src.database.db_models import AccountResource as AccountResourceDB
from src.Schemas.account_schema import AccountResource as AccountResourceSchema
from typing import List, Optional


async def save_account_resource(db: Session, address: str, resource: AccountResourceSchema):
    """
    Сохраняет или обновляет ресурсы аккаунта в базе данных.
    
    :param db: Сессия SQLAlchemy
    :param address: Адрес аккаунта
    :param resource: Pydantic-модель ресурсов
    :return: Сохранённая запись в БД
    """
    db_resource = db.query(AccountResourceDB).filter(AccountResourceDB.address == address).first()

    if db_resource:
        # Обновляем существующую запись
        for key, value in resource.dict(by_alias=True).items():
            setattr(db_resource, to_snake_case(key), value)
        db_resource.updated_at = datetime.utcnow()
    else:
        # Создаём новую
        db_resource = AccountResourceDB(
            address=address,
            **{to_snake_case(k): v for k, v in resource.dict(by_alias=True).items()}
        )
        db.add(db_resource)

    db.commit()
    db.refresh(db_resource)
    return db_resource


async def get_account_resource_by_address(db: Session, address: str) -> Optional[AccountResourceDB]:
    """
    Получает ресурсы аккаунта по адресу.
    
    :param db: Сессия SQLAlchemy
    :param address: Адрес аккаунта
    :return: Модель БД или None
    """
    return db.query(AccountResourceDB).filter(AccountResourceDB.address == address).first()


async def get_paginated_account_resources(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[AccountResourceDB]:
    """
    Получает список ресурсов аккаунтов с пагинацией.
    
    :param db: Сессия SQLAlchemy
    :param skip: Сколько записей пропустить (offset)
    :param limit: Максимальное количество записей
    :return: Список записей
    """
    return (
        db.query(AccountResourceDB)
        .order_by(AccountResourceDB.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def to_snake_case(camel_str: str) -> str:
    """
    Конвертирует camelCase в snake_case.
    """
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()