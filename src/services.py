from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from broker import NEW_KEY
from exceptions import DuplicatesIdempotencyKeyError, ResourceNotExistError
from repositories import OutboxRepository, PaymentsRepository
from schemas import CreatePaymentRequestSchema, CreatePaymentResponseSchema, DetailPaymentSchema, PaymentQueueBody

if TYPE_CHECKING:
    from models import PaymentModel


class PaymentService:
    """Сервис платежей."""

    def __init__(
        self,
        repository: PaymentsRepository,
        outbox_repository: OutboxRepository,
        session: AsyncSession,
    ) -> None:
        self._repository = repository
        self._outbox_repository = outbox_repository
        self._session = session

    async def retrieve(
        self,
        pk: UUID,
    ) -> DetailPaymentSchema:
        """Получение платежа по идентификатору."""
        payment: PaymentModel | None = await self._repository.retrieve(pk)
        if payment is None:
            raise ResourceNotExistError("payment")
        return DetailPaymentSchema.model_validate(payment)

    async def create(self, payload: CreatePaymentRequestSchema, idempotency_key: UUID) -> CreatePaymentResponseSchema:
        """Создание платежа и запись в outbox."""
        await self._check_idempotency_key(idempotency_key)
        new_payment = await self._repository.create(payload, idempotency_key)
        await self._outbox_repository.create(
            NEW_KEY,
            payload=PaymentQueueBody(payment_id=new_payment.payment_id),
        )
        await self._session.commit()
        return CreatePaymentResponseSchema.model_validate(new_payment)

    async def _check_idempotency_key(
        self,
        idempotency_key: UUID,
    ) -> None:
        payment = await self._repository.check_idempotency_key(idempotency_key)
        if payment:
            raise DuplicatesIdempotencyKeyError
