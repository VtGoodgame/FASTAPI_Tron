from aiohttp import ClientSession, ClientError
import asyncio
import aiohttp 
from typing import Any, Dict, Optional
from fastapi import  HTTPException
import logging
import json
from src import consts as c
import redis

REDIS = redis.Redis(
    host=c.REDIS_HOST,
    port=c.REDIS_PORT,
    decode_responses=True,
    username="default",
    password=c.REDIS_PASSWORD,
)

# Настройка асинхронного логирования
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
                logger.info(f"Успешный запрос к {endpoint}")
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
        REDIS.set(f"account_info:{address}", "Fetching...")
        try:
            account_info = await self._make_request(f"accounts/{address}")
            REDIS.set(f"account_info:{address}", json.dumps(account_info))
            return await self._make_request(f"accounts/{address}")
        except HTTPException as e:
            logger.error(f"Ошибка при получении информации об аккаунте: {str(e)}")
            REDIS.set(f"account_info:{address}", "Error")
            raise e

    async def get_wallet_transactions(self, address: str) -> Dict[str, Any]:
        """Асинхронно получить транзакции кошелька"""
        if not address:
            logger.error("Пустой параметр address")
            raise HTTPException(status_code=400, detail="Address is required")
        REDIS.set(f"wallet_transactions:{address}", "Fetching...")
        try:
            transactions = await self._make_request(f"accounts/{address}/transactions")
            REDIS.set(f"wallet_transactions:{address}", json.dumps(transactions))
            return transactions 
        except HTTPException as e:
            logger.error(f"Ошибка при получении транзакций кошелька: {str(e)}")
            REDIS.set(f"wallet_transactions:{address}", "Error")