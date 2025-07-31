import asyncio
import json
from typing import Any, Dict, Optional
from fastapi import HTTPException
import logging
import aioredis
from aiohttp import ClientSession
import aiohttp

from src import consts as c

# Настройка асинхронного Redis
redis_client = aioredis.from_url(
    f"redis://{c.REDIS_HOST}:{c.REDIS_PORT}",
    password=c.REDIS_PASSWORD,
    decode_responses=True,
    username="default",
    # encoding="utf-8",
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncTronAPIHandler:
    def __init__(self, base_url: str = c.BASE_URL):
        self.base_url = base_url.strip()
        self.session = None

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get("message", "Неизвестная ошибка")
                    except Exception:
                        error_msg = await response.text()
                    logger.error(f"Ошибка API: {error_msg}")
                    raise HTTPException(status_code=response.status, detail=error_msg)
                return await response.json()

        except asyncio.TimeoutError:
            logger.error("Таймаут запроса")
            raise HTTPException(status_code=504, detail="Request timeout")

        except aiohttp.ClientConnectionError as e:
            logger.error(f"Ошибка соединения: {str(e)}")
            raise HTTPException(status_code=503, detail="Service unavailable")

        except Exception as e:
            logger.error(f"Неизвестная ошибка: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal error")


class AsyncAccountService(AsyncTronAPIHandler):
    CACHE_TTL = 300  # 5 минут

    async def get_account_info(self, address: str) -> Dict[str, Any]:
        if not address:
            logger.error("Пустой параметр address")
            raise HTTPException(status_code=400, detail="Address is required")

        cache_key = f"account_info:{address}"
        cached = await redis_client.get(cache_key)
        if cached and cached not in ("Fetching...", "Error"):
            logger.info(f"Cache hit для {address}")
            return json.loads(cached)

        try:
            account_info = await self._make_request(f"accounts/{address}")
            await redis_client.set(cache_key, json.dumps(account_info), ex=self.CACHE_TTL)
            return account_info
        except HTTPException as e:
            logger.error(f"Ошибка при получении информации об аккаунте: {str(e)}")
            await redis_client.set(cache_key, "Error", ex=60)
            raise e

    async def get_wallet_transactions(self, address: str) -> Dict[str, Any]:
        if not address:
            logger.error("Пустой параметр address")
            raise HTTPException(status_code=400, detail="Address is required")

        cache_key = f"wallet_transactions:{address}"
        cached = await redis_client.get(cache_key)
        if cached and cached not in ("Fetching...", "Error"):
            logger.info(f"Cache hit для транзакций {address}")
            return json.loads(cached)

        try:
            transactions = await self._make_request(f"accounts/{address}/transactions")
            await redis_client.set(cache_key, json.dumps(transactions), ex=self.CACHE_TTL)
            return transactions
        except HTTPException as e:
            logger.error(f"Ошибка при получении транзакций: {str(e)}")
            await redis_client.set(cache_key, "Error", ex=60)
            raise e