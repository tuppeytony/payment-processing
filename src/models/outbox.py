import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class OutboxModel(Base):
    """Служебная модель для outbox."""

    __tablename__ = "outbox"

    outbox_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        comment="Идентификатор",
        server_default=text("gen_random_uuid()"),
    )
    event_type: Mapped[str] = mapped_column(comment="Тип события")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON(), comment="Данные о платеже")
    created_at: Mapped[datetime] = mapped_column(comment="Дата создания")
    processing_date: Mapped[datetime | None] = mapped_column(comment="Дата обработки")
    status: Mapped[str] = mapped_column(comment="Статус операции")
