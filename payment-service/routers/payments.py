from fastapi import APIRouter
from pydantic import BaseModel
from services.rabbitmq import publish_payment_confirmed

router = APIRouter(prefix="/payments", tags=["Payments"])

class DepositRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "ARS"

@router.post("/deposit")
async def create_deposit(request: DepositRequest):
    # Acá podrías validar, guardar logs, etc.
    publish_payment_confirmed(
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency
    )
    return {"status": "success", "message": "Payment confirmed event emitted"}
