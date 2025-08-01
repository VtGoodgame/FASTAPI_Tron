import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    with patch("main.get_redis", new_callable=AsyncMock) as mock:
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = True
        mock.return_value = redis_mock
        yield redis_mock

@pytest.fixture
def mock_db():
    with patch("main.get_db", return_value=MagicMock()) as mock:
        yield mock.return_value

@pytest.fixture
def mock_aiohttp_session():
    with patch("main.get_aiohttp_session", new_callable=AsyncMock) as mock:
        yield mock