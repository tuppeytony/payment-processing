from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import OutboxRepository, PaymentsRepository
from services import PaymentService
from storages import async_session


async def get_postgres() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии."""
    async with async_session() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_postgres)]


def get_idempotency_key(idempotency_key: Annotated[UUID, Header(default_factory=uuid4)]) -> UUID:
    """Получение ключа идемпотентности."""
    return idempotency_key


@lru_cache
def get_payment_repository(session: Session) -> PaymentsRepository:
    """Получение репозитория платежей."""
    return PaymentsRepository(session)


@lru_cache
def get_outbox_repository(session: Session) -> OutboxRepository:
    """Получение репозитория outbox."""
    return OutboxRepository(session)


@lru_cache
def get_payment_service(
    repository: Annotated[PaymentsRepository, Depends(get_payment_repository)],
    outbox_repository: Annotated[OutboxRepository, Depends(get_outbox_repository)],
    session: Session,
) -> PaymentService:
    """Получение сервиса платежей."""
    return PaymentService(repository, outbox_repository, session)
