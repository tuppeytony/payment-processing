import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums import OutboxEventStatus, PaymentStatus
from models import OutboxModel, PaymentModel
from schemas import CreatePaymentRequestSchema, PaymentQueueBody


class PaymentsRepository:
    """Репозиторий для платежей."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def retrieve(
        self,
        pk: UUID,
    ) -> PaymentModel | None:
        """Получение записи по идентификатору."""
        return await self._session.get(PaymentModel, pk)

    async def create(
        self,
        payload: CreatePaymentRequestSchema,
        idempotency_key: UUID,
    ) -> PaymentModel:
        """Создание платежа."""
        new_payment = PaymentModel(
            payment_id=uuid4(),
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            payment_metadata=payload.metadata,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            webhook_url=str(payload.webhook_url),
            creation_at=datetime.datetime.now(),
            processing_date=None,
        )
        self._session.add(new_payment)
        return new_payment

    async def check_idempotency_key(self, idempotency_key: UUID) -> PaymentModel | None:
        """Проверка ключа идемпотентности."""
        stmt = select(PaymentModel).where(PaymentModel.idempotency_key == idempotency_key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class OutboxRepository:
    """Репозиторий для служебной таблицы outbox."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        event_type: str,
        payload: PaymentQueueBody,
    ) -> None:
        """Создание записи в outbox таблице."""
        new_outbox = OutboxModel(
            created_at=datetime.datetime.now(),
            event_type=event_type,
            payload=payload.model_dump(mode="json"),
            status=OutboxEventStatus.PENDING,
        )
        self._session.add(new_outbox)

    async def pending(self, limit: int = 50) -> list[OutboxModel]:
        """Получение записей готовы для отправки в очередь."""
        stmt = (
            select(OutboxModel)
            .where(
                OutboxModel.processing_date.is_(None),
                OutboxModel.status == OutboxEventStatus.PENDING,
            )
            .order_by(OutboxModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list((await self._session.scalars(stmt)).all())

    @staticmethod
    async def mark_published(event: OutboxModel) -> None:
        """Отметка, что сообщение было отправлено."""
        event.processing_date = datetime.datetime.now()
        event.status = OutboxEventStatus.PUBLISHED

    @staticmethod
    async def mark_failed(event: OutboxModel) -> None:
        """Отметка, что сообщение не удалось отправить."""
        event.processing_date = datetime.datetime.now()
        event.status = OutboxEventStatus.FAILED
