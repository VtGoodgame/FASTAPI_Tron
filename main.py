from src import consts as c
import json
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from aiohttp import ClientSession, ClientError
import asyncio

# Настройка асинхронного логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncTronAPIHandler:
    """Асинхронный класс для обработки запросов к API Tron"""
    
    def __init__(self, base_url: str = c.BASE_URL):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        """Инициализация асинхронной сессии при входе в контекст"""
        self.session = ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        if self.session:
            await self.session.close()
            
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Асинхронный базовый метод для выполнения запросов"""
        try:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status != 200:
                    error_data = await response.json()
                    error_msg = error_data.get("message", "Неизвестная ошибка")
                    logger.error(f"Ошибка API: {error_msg}")
                    raise HTTPException(status_code=response.status, detail=error_msg)
                    
                return await response.json()
                
        except ClientError as e:
            logger.error(f"Ошибка соединения: {str(e)}")
            raise HTTPException(status_code=503, detail="Service unavailable")
        except json.JSONDecodeError:
            logger.error("Ошибка декодирования JSON")
            raise HTTPException(status_code=500, detail="Invalid JSON response")
        except asyncio.TimeoutError:
            logger.error("Таймаут запроса")
            raise HTTPException(status_code=504, detail="Request timeout")

class AsyncAccountService(AsyncTronAPIHandler):
    """Асинхронный сервис для работы с аккаунтами Tron"""
    
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Асинхронно получить информацию об аккаунте"""
        if not address:
            logger.error("Пустой параметр address")
            raise HTTPException(status_code=400, detail="Address is required")
        
        return await self._make_request(f"accounts/{address}")

    async def get_wallet_transactions(self, address: str) -> Dict[str, Any]:
        """Асинхронно получить транзакции кошелька"""
        if not address:
            logger.error("Пустой параметр address")
            raise HTTPException(status_code=400, detail="Address is required")
        
        return await self._make_request(f"accounts/{address}/transactions/trc20")

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
    app.state.account_service = AsyncAccountService()
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
