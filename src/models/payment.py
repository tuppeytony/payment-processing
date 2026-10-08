import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class PaymentModel(Base):
    """Таблица платежей."""

    __tablename__ = "payment"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        comment="Идентификатор платежа",
        server_default=text("gen_random_uuid()"),
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="Сумма")
    currency: Mapped[str] = mapped_column(comment="Валюта")
    description: Mapped[str | None] = mapped_column(comment="Описание платежа")
    payment_metadata: Mapped[JSON] = mapped_column("metadata", JSON(), comment="Метаданные")
    status: Mapped[str] = mapped_column(comment="Статус")
    idempotency_key: Mapped[uuid.UUID] = mapped_column(UUID(), comment="Ключ идемпотентности", unique=True)
    webhook_url: Mapped[str] = mapped_column(comment="WEBHOOK URL")
    creation_at: Mapped[datetime] = mapped_column(comment="Дата создания")
    processing_date: Mapped[datetime | None] = mapped_column(comment="Дата обработки")
