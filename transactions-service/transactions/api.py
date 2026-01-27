from ninja import Router
from .models import Transaction, Outbox
import json
from .schemas import TransactionCreate, TransactionOut, StatusUpdate
from typing import Optional
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404

router = Router()


@router.get("/transactions", response=list[TransactionOut])
def list_transactions(request, user_id: Optional[str] = None):
    qs = Transaction.objects.all()
    if user_id:
        qs = qs.filter(payer_user_id=user_id) | qs.filter(payee_user_id=user_id)
    return list(qs)


@router.post("/transactions/transfer", response=TransactionOut)
def transfer(request, payload: TransactionCreate):
    # idempotency handling: return existing transaction when idempotency_key matches
    existing = Transaction.objects.filter(idempotency_key=payload.idempotency_key).first()
    if existing:
        return existing

    with db_transaction.atomic():
        tx = Transaction.objects.create(
            idempotency_key=payload.idempotency_key,
            payer_user_id=payload.payer_user_id,
            payee_user_id=payload.payee_user_id,
            amount=payload.amount,
            currency=payload.currency,
            reason=(payload.reason or ""),
            status=Transaction.Status.PENDING,
            saga_step=Transaction.SagaStep.PENDING,
        )
        # Create an outbox event for the transaction creation
        Outbox.objects.create(
            topic="transaction.created",
            payload={
                "transaction_id": str(tx.id),
                "idempotency_key": tx.idempotency_key,
                "payer_user_id": tx.payer_user_id,
                "payee_user_id": tx.payee_user_id,
                "amount": str(tx.amount),
                "currency": tx.currency,
                "status": tx.status,
            },
        )
    
    # 🚀 Disparar la saga inmediatamente (asíncrono)
    from tasks.saga_tasks import process_transaction_saga
    process_transaction_saga.apply_async(args=[str(tx.id)], countdown=1)
    
    return tx


@router.patch("/transactions/{tx_id}/status", response=TransactionOut)
def update_status(request, tx_id: str, payload: StatusUpdate):
    tx = get_object_or_404(Transaction, id=tx_id)
    tx.status = payload.status
    tx.save()
    # Publish/update an outbox event for completion/failure
    topic = "transaction.completed" if tx.status == Transaction.Status.COMPLETED else "transaction.failed"
    Outbox.objects.create(topic=topic, payload={
        "transaction_id": str(tx.id),
        "status": tx.status,
    })
    return tx


@router.post("/transactions/{tx_id}/retry", response=TransactionOut)
def retry_failed_transaction(request, tx_id: str):
    """Reinicia una Saga que falló (idempotent)"""
    tx = get_object_or_404(Transaction, id=tx_id)
    
    if tx.status != Transaction.Status.FAILED:
        return {"error": "Only failed transactions can be retried"}
    
    # Reset para reintentar
    tx.status = Transaction.Status.PENDING
    tx.saga_step = Transaction.SagaStep.PENDING
    tx.debit_idempotency_key = None
    tx.credit_idempotency_key = None
    tx.reason = ""
    tx.save()
    
    Outbox.objects.create(
        topic="transaction.retry_requested",
        payload={"transaction_id": str(tx.id)}
    )
    
    # Disparar saga nuevamente
    from tasks.saga_tasks import process_transaction_saga
    process_transaction_saga.apply_async(args=[str(tx.id)], countdown=2)
    
    return tx


@router.get("/outbox", response=list)
def list_outbox(request):
    return list(Outbox.objects.all())
