import json
import aiohttp
import redis.asyncio as aioredis
from typing import AsyncGenerator
from sqlalchemy.orm import Session 
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends

from src import consts as c
from src.database.db_models import Base
from src.database.database import  get_db, engine , create_tables
from src.database.crud_trx import save_account_resource, get_paginated_account_resources
from src.Schemas.account_schema import AccountResource

@asynccontextmanager
async def lifespan(app: FastAPI):
    session = aiohttp.ClientSession()
    app.state.session = session
    yield
    await session.close()

app = FastAPI(lifespan=lifespan,
                title="Использование API платформы Tron",
                description="Тестовое задание",
                version="0.3")

# Зависимость для Redis
async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    client = aioredis.Redis(
        host=c.REDIS_HOST,
        port=c.REDIS_PORT,
        password=c.REDIS_PASSWORD,
        db=0,
        decode_responses=True
    )
    try:
        yield client
    finally:
        await client.close()


# Зависимость
async def get_aiohttp_session() -> aiohttp.ClientSession:
    session = getattr(app.state, "session", None)
    if session is None:
        session = aiohttp.ClientSession()
        app.state.session= session
    return session

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Константы
CACHE_TTL = 300  # 5 минут
CACHE_KEY_PREFIX = "account_resource:"

async def startup_event():
    global session, redis_client
    session = aiohttp.ClientSession()
    redis_client = aioredis.from_url(
        f"redis://{c.REDIS_HOST}:{c.REDIS_PORT}",
        password=c.REDIS_PASSWORD,
        decode_responses=True,
        username="default"
    )
    # Создаём таблицы при старте
    create_tables()

async def shutdown_event():
    """Очистка при завершении приложения"""
    global session, redis_client
    if session:
        await session.close()
    if redis_client:
        await redis_client.close()

# Эндпоинт: Получить информацию об аккаунте с кешированием и сохранением 
@app.get(c.PREFIX + "/get_account_info/{address}", summary="Получить информацию по адресу")
async def get_account_info(address: str, db: Session = Depends(get_db), session: aiohttp.ClientSession = Depends(get_aiohttp_session), redis: aioredis.Redis = Depends(get_redis)):
    """
    1. Проверяет валидность адреса
    2. Проверяет кеш Redis
    3. Если нет в кеше — запрашивает у API
    4. Сохраняет в Redis и БД
    5. Возвращает данные
    """
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")

    # Валидация адреса
    try:
        async with session.post(c.CHECK_ADDRESS, json={"address": address}) as response:
            if response.status != 200:
                raise HTTPException(status_code=400, detail="Invalid response from address validation service")
            validation_data = await response.json()
            if not validation_data.get("result", False):
                raise HTTPException(status_code=400, detail="Invalid Tron address")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Address validation failed: {str(e)}")

    cache_key = f"{CACHE_KEY_PREFIX}{address}"

    # Проверка кеша
    cached = await redis.get(cache_key)
    if cached:
        return {
            "address": address,
            "exists": True,
            "resources": json.loads(cached),
            "from_cache": True
        }

    #  Запрос к API
    try:
        async with session.post(c.CHECK_ACCAUNT, json={"address": address}) as response:
            if response.status != 200:
                # Аккаунт не существует
                if response.status in (400, 404):
                    return {"address": address, "exists": False, "resources": None}
                raise HTTPException(status_code=response.status, detail="Failed to fetch account resources")

            account_data = await response.json()

        # Валидация
        resource_model = AccountResource(**account_data)

        # Сохранение в Redis
        await redis.setex(
            cache_key,
            CACHE_TTL,
            resource_model.json(by_alias=True)
        )

        #Сохранение в PostgreSQL
        await save_account_resource(db, address, resource_model)

        return {
            "address": address,
            "exists": True,
            "resources": account_data,
            "from_cache": False
        }

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


# Эндпоинт: Получить список информации по последним запросам с пагинацией 
@app.get(c.PREFIX + "/account-resources/", summary="Получить список информации по последним запросам")
async def get_account_resources_paginated(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список информации по последним запросам с пагинацией.
    """
    resources = await get_paginated_account_resources(db, skip=skip, limit=limit)
    return {
        "data": resources,
        "skip": skip,
        "limit": limit,
        "total": len(resources)
    }