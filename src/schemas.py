from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, Json

from enums import CurrencyTypes, PaymentStatus


class CreatePaymentRequestSchema(BaseModel):
    """Схема для создания платежа."""

    amount: Decimal = Field(description="Сумма", gt=0, max_digits=10, decimal_places=2)
    currency: CurrencyTypes = Field(description="Валюта")
    description: str | None = Field(default=None, description="Описание")
    metadata: Json[dict[str, Any]] = Field(description="Метаданные")
    webhook_url: HttpUrl = Field(description="Адрес веб хука")


class CreatePaymentResponseSchema(BaseModel):
    """Схема для ответа после создания платежа."""

    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID = Field(description="Идентификатор платежа")
    status: PaymentStatus = Field(description="Статус платежа")
    creation_at: datetime = Field(description="Дата создания")


class DetailPaymentSchema(BaseModel):
    """Схема для детального представления платежа."""

    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID = Field(description="Идентификатор платежа")
    amount: Decimal = Field(description="Сумма")
    currency: CurrencyTypes = Field(description="Валюта")
    description: str = Field(description="Описание")
    metadata: dict[str, Any] = Field(description="Метаданные", validation_alias="payment_metadata")
    status: PaymentStatus = Field(description="Статус платежа")
    idempotency_key: UUID = Field(description="Ключ идемпотентности")
    webhook_url: HttpUrl = Field(description="Адрес веб хука")
    creation_at: datetime = Field(description="Дата создания")
    processing_date: datetime | None = Field(description="Дата обработки")


class PaymentWebhookRequest(BaseModel):
    """Схема для отправки данных на внешний адрес."""

    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID = Field(description="Идентификатор платежа")
    amount: Decimal = Field(description="Сумма", gt=0, max_digits=10, decimal_places=2)
    currency: CurrencyTypes = Field(description="Валюта")
    description: str | None = Field(default=None, description="Описание")
    metadata: dict[str, Any] = Field(description="Метаданные", validation_alias="payment_metadata")
    creation_at: datetime = Field(description="Дата создания")


class PaymentQueueBody(BaseModel):
    """Тело сообщения для очереди платежей."""

    payment_id: UUID = Field(description="Идентификатор платежа")
