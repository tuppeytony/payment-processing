from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, status

from dependencies import get_idempotency_key, get_payment_service
from schemas import CreatePaymentRequestSchema, CreatePaymentResponseSchema, DetailPaymentSchema
from services import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Создание платежа.",
)
async def create_payments(
    payload: Annotated[CreatePaymentRequestSchema, Body()],
    idempotency_key: Annotated[UUID, Depends(get_idempotency_key)],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> CreatePaymentResponseSchema:
    """Создание платежа."""
    return await service.create(payload, idempotency_key)


@router.get("/{payment_id}", summary="Получение платежа по идентификатору.")
async def retrieve_payment(
    payment_id: Annotated[UUID, Path(description="Идентификатор платежа")],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> DetailPaymentSchema:
    """Получение платежа по идентификатору."""
    return await service.retrieve(payment_id)
