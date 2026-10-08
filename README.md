# Асинхронный сервис процессинга платежей

## Запуск проекта
Для развертывания всей инфраструктуры (API, Consumer, Релей Outbox, PostgreSQL, RabbitMQ) выполните команду:
```bash
docker-compose up --build
```

## Примеры запросов к API

### 1. Создание платежа
**Маршрут:** `POST /api/v1/payments`
**Заголовки:**
- `X-API-Key: super-secret-static-key`
- `Idempotency-Key: unique-uuid-v4-key-100`

**Тело запроса (JSON):**
```json
{
  "amount": 2500.50,
  "currency": "RUB",
  "description": "Оплата подписки",
  "metadata": {
    "user_id": 42,
    "tier": "premium"
  },
  "webhook_url": "https://webhook.site"
}
```

**Ответ (202 Accepted):**
```json
{
  "payment_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "pending",
  "created_at": "2026-10-05T12:00:00.123456"
}
```

### 2. Получение информации о платеже
**Маршрут:** `GET /api/v1/payments/{payment_id}`
**Заголовки:**
- `X-API-Key: super-secret-static-key`

**Ответ (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "amount": 2500.50,
  "currency": "RUB",
  "description": "Оплата подписки",
  "metadata": {
    "user_id": 42,
    "tier": "premium"
  },
  "status": "succeeded",
  "idempotency_key": "unique-uuid-v4-key-100",
  "webhook_url": "https://webhook.site",
  "created_at": "2026-10-05T12:00:00.123456",
  "processed_at": "2026-10-05T12:00:04.567890"
}
```
