import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Annotated

import httpx
from faststream import Depends, FastStream, Header
from faststream.rabbit import RabbitBroker

from broker import DLQ_KEY, DLX, EXCHANGE, NEW_QUEUE, declare_topology, retry_queue
from config import app_settings, rabbit_settings
from enums import PaymentStatus
from exceptions import ResourceNotExistError
from models import PaymentModel
from schemas import PaymentQueueBody, PaymentWebhookRequest
from storages import async_session

log = logging.getLogger("consumer")

broker = RabbitBroker(rabbit_settings.dsn)
app = FastStream(broker)


@app.after_startup
async def _setup() -> None:
    await declare_topology(broker)


def get_x_attempt(x_attempt: Annotated[int, Header("x-attempt")]) -> int:
    """Получение количество отправок в очередь."""
    return x_attempt


async def _emulate_gateway() -> PaymentStatus:
    await asyncio.sleep(random.uniform(2, 5))
    success_value = 0.9
    return PaymentStatus.SUCCEEDED if random.random() < success_value else PaymentStatus.FAILED


async def _process(payment_id: uuid.UUID) -> None:
    async with async_session() as session:
        payment: PaymentModel | None = await session.get(PaymentModel, payment_id, with_for_update=True)
        if payment is None:
            raise ResourceNotExistError("payment")
        need_processing = payment.status == PaymentStatus.PENDING

        if need_processing:
            result = await _emulate_gateway()
            if payment.status == PaymentStatus.PENDING:
                payment.status = result
                payment.processing_date = datetime.now()

        body = PaymentWebhookRequest.model_validate(payment)
        url = payment.webhook_url

    async with httpx.AsyncClient(timeout=app_settings.webhook_timeout) as client:
        resp = await client.post(url, json=body.model_dump_json())
        resp.raise_for_status()

        payment.processing_date = datetime.now()


@broker.subscriber(NEW_QUEUE, EXCHANGE)
async def handle_payment(
    payment: PaymentQueueBody,
    attempt: Annotated[int, Depends(get_x_attempt)],
) -> None:
    """Обработка платежа."""
    try:
        await _process(payment.payment_id)
        log.info("payment %s processed (attempt %d)", payment.payment_id, attempt)
    except Exception as exc:
        log.warning("payment %s failed on attempt %d: %r", payment.payment_id, attempt, exc)
        if attempt < app_settings.max_attempts:
            await broker.publish(
                payment.model_dump(),
                queue=retry_queue(attempt),
                headers={"x-attempt": attempt + 1},
                persist=True,
            )
        else:
            await broker.publish(
                payment.model_dump(),
                exchange=DLX,
                routing_key=DLQ_KEY,
                headers={"x-attempt": attempt, "x-error": repr(exc)[:500]},
                persist=True,
            )
            log.exception("payment %s sent to DLQ", payment.payment_id)
