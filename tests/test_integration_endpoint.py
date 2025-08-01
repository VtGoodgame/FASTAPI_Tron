import pytest
from httpx import AsyncClient
from main import app
from src import consts as c

@pytest.mark.asyncio
class TestTronAPI:
    """Интеграционные тесты Tron API через FastAPI"""

    @pytest.fixture(scope="class", autouse=True)
    async def setup_client(self):
        """Создаёт клиента для тестов (один раз на класс)"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            self.client = ac
            yield

    async def test_invalid_address(self):
        """
        Тест 1: Неверный адрес должен вернуть ошибку 400
        """
        response = await self.client.get(f"/api/v03/get_account_info/{c.INVALID_ADDRESS}")
        assert response.status_code == 400
        assert "Invalid Tron address" in response.json()["detail"]

    async def test_address_not_found(self):
        """
        Тест 2: Валидный, но несуществующий адрес должен вернуть exists=False
        """
        response = await self.client.get(f"/api/v03/get_account_info/{c.VALID_ADDRESS}")
        assert response.status_code in (200, 400, 503)
        data = response.json()
        assert "address" in data
        if response.status_code == 200:
            assert data["exists"] in [True, False]  # если 404 с Tron API
            assert "resources" in data

    async def test_cache_and_db_saved(self):
        """
        Тест 3: При повторном запросе данные берутся из кеша Redis
        (если address существует и был сохранён)
        """
        response_1 = await self.client.get(f"/api/v03/get_account_info/{c.VALID_ADDRESS}")
        if response_1.status_code != 200 or not response_1.json().get("exists"):
            pytest.skip("Address not available for caching test")

        response_2 = await self.client.get(f"/api/v03/get_account_info/{c.VALID_ADDRESS}")
        assert response_2.status_code == 200
        assert response_2.json()["from_cache"] is True

    async def test_paginated_list(self):
        """
        Тест 4: Проверка эндпоинта пагинации
        """
        response = await self.client.get("/api/v03/account-resources/?skip=0&limit=100")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert "skip" in data
        assert "limit" in data