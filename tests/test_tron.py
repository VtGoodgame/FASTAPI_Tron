import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from src import consts as c

# -------------------------------
# Фикстуры: тестовые данные
# -------------------------------

@pytest.fixture
def account_info_json():
    return {
        "address": "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8",
        "balance": 15000000,
        "trc20": {
            "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": "15000000"
        },
        "latest_opration_time": 1712016000000
    }


@pytest.fixture
def trc20_response_json():
    return {
        "data": [
            {
                "transaction_id": "a4f8d9e7c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7",
                "token_info": {
                    "symbol": "USDT",
                    "address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                    "decimals": 6,
                    "name": "Tether USD"
                },
                "block_timestamp": 1712016000000,
                "from": "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8",
                "to": "TQm2n1o0p9o8i7u6y5t4r3e2w1q2w3e4r5t6y7u8i",
                "type": "Transfer",
                "value": "15000000"
            }
        ],
        "success": True,
        "meta": {
            "at": 1712016050000,
            "page_size": 20,
            "fingerprint": "abc123xyz",
            "links": {
                "next": "https://..."
            }
        }
    }


# -------------------------------
# Фикстуры: моки
# -------------------------------

@pytest.fixture
def service():
    from src.async_handler import AsyncAccountService
    return AsyncAccountService(base_url=c.BASE_URL)

@pytest.fixture
def handler():
    from src.async_handler import AsyncTronAPIHandler
    return AsyncTronAPIHandler(base_url=c.BASE_URL)

@pytest.fixture(autouse=True)
def mock_redis():
    with patch("src.async_handler.redis_client") as mock:
        mock.get.return_value = None  # по умолчанию
        yield mock


@pytest.fixture
def mock_session():
    with patch("src.async_handler.ClientSession") as mock:
        session = MagicMock()
        mock.return_value.__aenter__.return_value = session

        response = MagicMock()
        session.get.return_value.__aenter__.return_value = response

        response.json = AsyncMock()
        response.text = AsyncMock()

        yield session, response


# -------------------------------
# Тесты
# -------------------------------

@pytest.mark.asyncio
async def test_get_account_info_cache_hit(service, mock_redis, account_info_json):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = json.dumps(account_info_json)  

    async with service:
        result = await service.get_account_info(address)

    assert result == account_info_json
    mock_redis.get.assert_called_once_with(f"account_info:{address}")


@pytest.mark.asyncio
async def test_get_account_info_cache_miss(service, mock_redis, mock_session, account_info_json):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = None  

    
    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.json = AsyncMock(return_value=account_info_json)
    response_mock.status = 200  

    async with service:
        result = await service.get_account_info(address)

    assert result == account_info_json
    mock_redis.set.assert_called_once_with(
        f"account_info:{address}",
        json.dumps(account_info_json),
        ex=300
    )


@pytest.mark.asyncio
async def test_get_account_info_api_error(service, mock_redis, mock_session):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = None

    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.status = 404
    response_mock.json = AsyncMock(return_value={"message": "Not found"})

    async with service:
        with pytest.raises(HTTPException) as exc_info:
            await service.get_account_info(address)

    assert exc_info.value.status_code == 404 
    mock_redis.set.assert_called_once_with(f"account_info:{address}", "Error", ex=60)


@pytest.mark.asyncio
async def test_get_account_info_connection_error(service, mock_redis, mock_session):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = None
    mock_session.get.side_effect = asyncio.TimeoutError()

    async with service:
        with pytest.raises(HTTPException) as exc_info:
            await service.get_account_info(address)

    assert exc_info.value.status_code == 504
    mock_redis.set.assert_called_once_with(f"account_info:{address}", "Error", ex=60)


# -------------------------------
# Тесты: get_wallet_transactions
# -------------------------------

@pytest.mark.asyncio
async def test_get_wallet_transactions_cache_hit(service, mock_redis, trc20_response_json):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = json.dumps(trc20_response_json)  

    async with service:
        result = await service.get_wallet_transactions(address)

    assert result == trc20_response_json
    mock_redis.get.assert_called_once_with(f"wallet_transactions:{address}")


@pytest.mark.asyncio
async def test_get_wallet_transactions_cache_miss(service, mock_redis, mock_session, trc20_response_json):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = None

    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.json = AsyncMock(return_value=trc20_response_json)
    response_mock.status = 200

    async with service:
        result = await service.get_wallet_transactions(address)

    assert result == trc20_response_json
    mock_redis.set.assert_called_once_with(
        f"wallet_transactions:{address}",
        json.dumps(trc20_response_json),
        ex=300
    )


@pytest.mark.asyncio
async def test_get_wallet_transactions_api_error(service, mock_redis, mock_session):
    address = "TQn9Y2oZ6NsJQqJtKqj5qjXy5WZ1a2b3c4d5e6f7g8"
    mock_redis.get.return_value = None

    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.status = 500
    response_mock.json = AsyncMock(return_value={"message": "Server error"})

    async with service:
        with pytest.raises(HTTPException) as exc_info:
            await service.get_wallet_transactions(address)

    assert exc_info.value.status_code == 500 
    mock_redis.set.assert_called_once_with(f"wallet_transactions:{address}", "Error", ex=60)


# -------------------------------
# Тесты: _make_request
# -------------------------------

@pytest.mark.asyncio
async def test_make_request_success(service, mock_session):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": "ok"})
    mock_session.get.return_value.__aenter__.return_value.status = 200

    async with service:
        result = await service._make_request("/test")

    assert result == {"data": "ok"}


@pytest.mark.asyncio
async def test_make_request_http_error(service, mock_session):
    response_mock = mock_session.get.return_value.__aenter__.return_value
    response_mock.status = 400
    response_mock.json = AsyncMock(return_value={"message": "Bad request"})

    async with service:
        with pytest.raises(HTTPException) as exc_info:
            await service._make_request("/test")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bad request"


@pytest.mark.asyncio
async def test_make_request_timeout(service, mock_session):
    mock_session.get.side_effect = asyncio.TimeoutError()

    async with service:
        with pytest.raises(HTTPException) as exc_info:
            await service._make_request("/test")

    assert exc_info.value.status_code == 504