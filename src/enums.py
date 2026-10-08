from enum import StrEnum


class CurrencyTypes(StrEnum):
    """Виды валют."""

    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class PaymentStatus(StrEnum):
    """Статус платежа."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OutboxEventStatus(StrEnum):
    """Статус обработки платежа."""

    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
