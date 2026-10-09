import asyncio
import logging

from faststream.rabbit import RabbitBroker

from broker import EXCHANGE, NEW_KEY, broker, declare_topology
from common import configure_logging
from config import app_settings
from repositories import OutboxRepository
from storages import async_session

log = logging.getLogger("outbox")


async def publish_batch(broker: RabbitBroker) -> None:
    """Множественная отправка в очередь."""
    async with async_session() as session, session.begin():
        events = await OutboxRepository(session).pending()
        for event in events:
            try:
                await broker.publish(
                    event.payload,
                    exchange=EXCHANGE,
                    routing_key=NEW_KEY,
                    message_id=str(event.outbox_id),
                    headers={"x-attempt": 1},
                    persist=True,
                )
            except Exception:
                await OutboxRepository.mark_failed(event)
                log.exception("Could not publish outbox event %s", event.outbox_id)
            else:
                log.info("Event published")
                await OutboxRepository.mark_published(event)


async def run_relay(broker: RabbitBroker) -> None:
    """Запуск отправки в очередь."""
    log.info("Outbox worker is started")
    while True:
        try:
            await publish_batch(broker)
        except Exception:
            log.exception("outbox relay error, will retry")
        await asyncio.sleep(2)


async def main() -> None:
    """."""
    async with broker:
        await asyncio.gather(declare_topology(broker), broker.start(), run_relay(broker))


if __name__ == "__main__":
    configure_logging(app_settings.log_level)
    asyncio.run(main())
