from fastapi import APIRouter
from pydantic import BaseModel
from services.rabbitmq import publish_payment_confirmed
from db.mongo import save_failed_payment

router = APIRouter(prefix="/payments", tags=["Payments"])

class DepositRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "ARS"

@router.post("/deposit")
async def create_deposit(request: DepositRequest):
    try:
        publish_payment_confirmed(
            user_id=request.user_id,
            amount=request.amount,
            currency=request.currency
        )
        return {"status": "success", "message": "Payment confirmed event emitted"}
    except Exception as e:
        # Si falla RabbitMQ, guardar el evento en MongoDB para reintento
        event_payload = {
            "user_id": request.user_id,
            "amount": request.amount,
            "currency": request.currency
        }
        save_failed_payment("payment.confirmed", event_payload, error=str(e))
        return {"status": "pending", "message": "RabbitMQ unavailable, event saved for retry", "error": str(e)}
