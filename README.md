# Асинхронный сервис процессинга платежей

## Запуск проекта
Для развертывания всей инфраструктуры выполните команду:
```bash
make run
```

Заголовок для аутентификации по дефолту secret

Пример запроса на создание платежа
```
curl --location 'http://localhost:8000/api/v1/payments' \
--header 'Content-Type: application/json' \
--header 'X-API-key: ••••••' \
--data '{
  "amount": 1,
  "currency": "rub",
  "description": "string",
  "metadata": "{\"additionalProp1\":{}}",
  "webhook_url": "https://example.com/"
}'
```

Получение платежа по идентификатору
```
curl --location 'http://localhost:8000/api/v1/payments/{payment_id}' \
--header 'Content-Type: application/json' \
--header 'X-API-key: ••••••'
```
