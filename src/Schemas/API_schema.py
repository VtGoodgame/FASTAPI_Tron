from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    """
    Информация о токене TRC20, участвующем в транзакции.
    """
    symbol: str = Field(..., description="Символ токена TRC20")
    address: str = Field(..., description="Адрес контракта TRC20")
    decimals: int = Field(..., description="Десятичные знаки токенов TRC20")
    name: str = Field(..., description="Имя токена TRC20")


class TransactionItem(BaseModel):
    """
    Единая запись транзакции TRC20.
    """
    transaction_id: str = Field(..., alias="transaction_id", description="Идентификатор транзакции")
    token_info: TokenInfo = Field(..., description="Метаданные токена")
    block_timestamp: int = Field(..., description="Временная метка блока в миллисекундах")
    from_: str = Field(..., alias="from", description="Адрес отправителя")
    to: str = Field(..., description="Адрес получателя")
    type: str = Field(..., description="Функция транзакции (например, перевод)")
    value: str = Field(..., description="Сумма, переведенная в виде строки (из-за больших чисел)")


class MetaLinks(BaseModel):
    """
    Ссылки с разбивкой по страницам в разделе "мета".
    """
    next: Optional[str] = Field(None, description="URL следующей страницы, если таковой имеется")


class Meta(BaseModel):
    """
    Метаданные об ответе.
    """
    at: int = Field(..., description="Временная метка ответа в миллисекундах")
    page_size: int = Field(..., description="Количество элементов на странице")
    fingerprint: Optional[str] = Field(None, description="Отпечаток пальца для следующего запроса")
    links: MetaLinks = Field(..., description="Ссылки на разбивку по страницам")


class TRC20TransactionsResponse(BaseModel):
    """
    Корневая модель, представляющая полный ответ от конечной точки транзакций TRC20.
    """
    data: List[TransactionItem] = Field(..., description="Список записей транзакций TRC20")
    success: bool = Field(..., description="Был ли запрос выполнен успешно")
    meta: Meta = Field(..., description="Метаданные об ответе")


def ms_to_datetime(ms: int) -> datetime:
    seconds = ms / 1000
    dt = datetime.utcfromtimestamp(seconds).replace(tzinfo=timezone.utc)
    return dt