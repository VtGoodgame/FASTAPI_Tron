from src import consts as c
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import aiohttp
from aiohttp import ClientSession
from . import AsyncTronAPIHandler as AsyncHandler
from src.database.models.db_models import Base
from src.database.database import engine


Base.metadata.create_all(bind=engine)

# Создание FastAPI приложения
app = FastAPI(
    title="Использование API платформы Tron",
    description="Тестовое задание",
    version="0.2"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    app.state.account_service = AsyncHandler.AsyncAccountService()
    app.state.account_service.session = ClientSession()

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении приложения"""
    if hasattr(app.state.account_service, 'session'):
        await app.state.account_service.session.close()

@app.get(c.Prefix + "/get_account_info/{address}", summary="Получить информацию по адресу")
async def get_account_info(address: str):
    """
    Получаем информацию об аккаунте пользователя с использованием адреса
    
    - **address**: адрес аккаунта (обязательный параметр)
    """
    return await app.state.account_service.get_account_info(address)

@app.get(c.Prefix + "/get_wallet_info/{address}", summary="Получить информацию по адресу")
async def get_wallet_info(address: str):
    """
    Получаем информацию о кошельке пользователя с использованием адреса
    
    - **address**: адрес аккаунта (обязательный параметр)
    """
    return await app.state.account_service.get_wallet_transactions(address)
