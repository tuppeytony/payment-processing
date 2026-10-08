from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from config import app_settings, rabbit_settings

broker = RabbitBroker(rabbit_settings.dsn)

NEW_KEY = "payments.new"
DLQ_KEY = "payments.dlq"

EXCHANGE = RabbitExchange("payments", type=ExchangeType.DIRECT, durable=True)
DLX = RabbitExchange("payments.dlx", type=ExchangeType.DIRECT, durable=True)

NEW_QUEUE = RabbitQueue(
    NEW_KEY,
    durable=True,
    routing_key=NEW_KEY,
    arguments={"x-dead-letter-exchange": DLX.name, "x-dead-letter-routing-key": DLQ_KEY},
)
DLQ_QUEUE = RabbitQueue(DLQ_KEY, durable=True, routing_key=DLQ_KEY)


def retry_delay_ms(attempt: int) -> int:
    """Задержка перед попыткой attempt+1 (attempt начинается с 1): base, base*2, base*4..."""
    return app_settings.retry_base_delay_ms * 2 ** (attempt - 1)


def retry_queue(attempt: int) -> RabbitQueue:
    """Очередь для переотправки."""
    return RabbitQueue(
        f"payments.retry.{attempt}",
        durable=True,
        arguments={
            "x-message-ttl": retry_delay_ms(attempt),
            "x-dead-letter-exchange": EXCHANGE.name,
            "x-dead-letter-routing-key": NEW_KEY,
        },
    )


async def declare_topology(broker: RabbitBroker) -> None:
    """Объявления топологии брокера."""
    exchange = await broker.declare_exchange(EXCHANGE)
    dlx = await broker.declare_exchange(DLX)

    new_q = await broker.declare_queue(NEW_QUEUE)
    await new_q.bind(exchange, routing_key=NEW_KEY)

    dlq = await broker.declare_queue(DLQ_QUEUE)
    await dlq.bind(dlx, routing_key=DLQ_KEY)

    for attempt in range(1, app_settings.max_attempts):
        await broker.declare_queue(retry_queue(attempt))
