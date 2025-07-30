from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from src.database.models.db_models import TRC20Transaction
from src.Schemas.API_schema import TransactionItem, TokenInfo, ms_to_datetime
from src.database.crud.crud_trx import (  
    save_transaction,
    get_transactions_by_address,
    get_last_100_transactions,
)


@pytest.fixture
def sample_transaction_item():
    return TransactionItem.model_construct(
        transaction_id="abc123",
        token_info=TokenInfo.model_construct(
            symbol="USDT",
            address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
            name="Tether USD",
            decimals=6,
        ),
        block_timestamp=1722384000000,
        from_="from_address",  
        to="to_address",
        type="Transfer",
        value="1000000",
    )


@pytest.fixture
def sample_db_transaction():
    """ объект модели TRC20Transaction"""
    return TRC20Transaction(
        transaction_id="abc123",
        token_symbol="USDT",
        token_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        token_name="Tether USD",
        token_decimals=6,
        block_timestamp=datetime(2025, 7, 30, tzinfo=timezone.utc),
        from_address="from_address",
        to_address="to_address",
        trx_type="Transfer",
        value="1000000",
    )


@pytest.mark.asyncio
async def test_save_transaction(sample_transaction_item):
    # Мокаем сессию
    mock_db = Mock(spec=Session)

    # Выполняем функцию
    result = await save_transaction(mock_db, sample_transaction_item)

    # Проверяем, что объект TRC20Transaction был корректно создан
    assert result.transaction_id == "abc123"
    assert result.token_symbol == "USDT"
    assert result.to_address == "to_address"
    assert result.block_timestamp == datetime(2025, 7, 30, tzinfo=timezone.utc)

    # Проверяем, что методы сессии были вызваны
    mock_db.add.assert_called_once_with(result)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_get_transactions_by_address():
    mock_db = Mock(spec=Session)
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    expected_result = ["trx1", "trx2"]

    # Настраиваем мок: db.query(...).filter(...).all() → возвращает список
    mock_filter.all.return_value = expected_result

    address = "my_address"
    result = await get_transactions_by_address(mock_db, address)

    # Проверяем результат
    assert result == expected_result

    # Проверяем цепочку вызовов
    mock_db.query.assert_called_once_with(TRC20Transaction)
    mock_query.filter.assert_called_once()
    filter_call = mock_query.filter.call_args[0][0]
    assert str(filter_call) == str(TRC20Transaction.to_address == address)
    mock_filter.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_last_100_transactions():
    mock_db = Mock(spec=Session)
    mock_query = mock_db.query.return_value
    mock_order = mock_query.order_by.return_value
    mock_limit = mock_order.limit.return_value
    expected_result = ["trx1", "trx2", "trx3"]

    # Настраиваем мок
    mock_limit.all.return_value = expected_result

    result = await get_last_100_transactions(mock_db)

    # Проверяем результат
    assert result == expected_result

    # Проверяем вызовы
    mock_db.query.assert_called_once_with(TRC20Transaction)
    mock_query.order_by.assert_called_once()
    order_call = mock_query.order_by.call_args[0][0]
    assert str(order_call) == str(TRC20Transaction.block_timestamp.desc())
    mock_order.limit.assert_called_once_with(100)
    mock_limit.all.assert_called_once()


@pytest.mark.asyncio
async def test_save_transaction_uses_ms_to_datetime(sample_transaction_item):
    mock_db = Mock(spec=Session)

    with patch("src.database.crud.crud_trx.ms_to_datetime") as mock_converter:
        expected_dt = datetime(2025, 7, 30, tzinfo=timezone.utc)
        mock_converter.return_value = expected_dt

        result = await save_transaction(mock_db, sample_transaction_item)

        mock_converter.assert_called_once_with(sample_transaction_item.block_timestamp)
        assert result.block_timestamp == expected_dt