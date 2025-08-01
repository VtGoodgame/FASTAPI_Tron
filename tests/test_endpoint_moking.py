import json
from unittest.mock import AsyncMock
from main import app, get_paginated_account_resources

mock_account_data = {
    "freeNetUsed": 100,
    "freeNetLimit": 5000,
    "NetUsed": 200,
    "NetLimit": 1000,
    "TotalNetLimit": 5000,
    "TotalNetWeight": 10000,
    "EnergyUsed": 0,
    "EnergyLimit": 1000,
    "TotalEnergyLimit": 10000,
    "TotalEnergyWeight": 15000,
    "tronPowerUsed": 0,
    "tronPowerLimit": 100,
    "assetNetUsed": {},
    "assetNetLimit": {}
}

mock_validation_response = {"result": True}

def test_get_account_info_cache_hit(client, mock_redis, mock_db, mock_aiohttp_session):
    address = "T123"
    mock_redis.get.return_value = json.dumps(mock_account_data)

    response = client.get(f"/api/v03/get_account_info/{address}")
    assert response.status_code == 200
    data = response.json()
    assert data["from_cache"] is True
    assert data["resources"] == mock_account_data

def test_get_account_info_cache_miss_valid_address(client, mock_aiohttp_session, mock_redis, mock_db):
    address = "T123"
    mock_validate_response = AsyncMock()
    mock_validate_response.status = 200
    mock_validate_response.json.return_value = mock_validation_response

    mock_resource_response = AsyncMock()
    mock_resource_response.status = 200
    mock_resource_response.json.return_value = mock_account_data

    mock_aiohttp_session.return_value.post.side_effect = [mock_validate_response, mock_resource_response]
    mock_redis.get.return_value = None

    response = client.get(f"/api/v03/get_account_info/{address}")
    assert response.status_code == 200
    data = response.json()
    assert data["from_cache"] is False
    assert data["address"] == address

def test_get_account_info_invalid_address(client, mock_aiohttp_session):
    address = "invalid"
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"result": False}
    mock_aiohttp_session.return_value.post.return_value = mock_response

    response = client.get(f"/api/v03/get_account_info/{address}")
    assert response.status_code == 400
    assert "Invalid Tron address" in response.json()["detail"]

def test_get_account_info_account_not_exists(client, mock_aiohttp_session, mock_redis):
    address = "T123"
    validate_resp = AsyncMock()
    validate_resp.status = 200
    validate_resp.json.return_value = mock_validation_response

    resource_resp = AsyncMock()
    resource_resp.status = 404

    mock_aiohttp_session.return_value.post.side_effect = [validate_resp, resource_resp]
    mock_redis.get.return_value = None

    response = client.get(f"/api/v03/get_account_info/{address}")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is False

def test_get_account_resources_paginated(client, mock_db):
    mock_resources = [{"address": "T123", "free_net_used": 100}]
    app.dependency_overrides[get_paginated_account_resources] = lambda: mock_resources

    response = client.get("/api/v03/account-resources/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["address"] == "T123"

    app.dependency_overrides = {}