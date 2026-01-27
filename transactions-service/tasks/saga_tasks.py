"""
Celery tasks para procesar transacciones mediante Saga Pattern
"""
import os
from celery import Celery, shared_task
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transactions_service.settings")

app = Celery("transactions_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@shared_task(name="process_transaction_saga", bind=True, max_retries=3)
def process_transaction_saga(self, transaction_id: str):
    """
    Celery task que ejecuta la saga de transacción.
    Reintentar 3 veces con backoff exponencial si falla.
    """
    from transactions.saga_orchestrator import TransactionSaga
    
    saga = TransactionSaga()
    result = saga.execute(transaction_id)
    
    if not result["success"]:
        # Retry con backoff exponencial
        retry_count = self.request.retries
        countdown = 60 * (2 ** retry_count)  # 60s, 120s, 240s
        
        try:
            raise self.retry(countdown=countdown)
        except self.MaxRetriesExceededError:
            # Si se agotaron los reintentos, publicar a DLQ
            from transactions.models import Outbox
            from transactions.models import Transaction
            
            tx = Transaction.objects.get(id=transaction_id)
            Outbox.objects.create(
                topic="transaction.deadletter",
                payload={
                    "transaction_id": transaction_id,
                    "error": result.get("error"),
                    "reason": tx.reason,
                    "needs_manual_review": True
                }
            )
    
    return result


@shared_task(name="consume_transaction_events")
def consume_transaction_events():
    """
    Celery task para consumir eventos de transacción del Outbox
    y procesarlos mediante la Saga.
    Se ejecuta periódicamente (via Celery Beat).
    """
    from transactions.models import Outbox, Transaction
    
    # Buscar eventos no publicados de tipo transaction.created
    pending_events = Outbox.objects.filter(
        topic="transaction.created",
        published_at__isnull=True
    )[:100]  # Procesar en lotes de 100
    
    count = 0
    for event in pending_events:
        transaction_id = event.payload.get("transaction_id")
        if transaction_id:
            # Disparar la saga
            process_transaction_saga.apply_async(
                args=[transaction_id],
                countdown=1  # Ejecutar en 1 segundo
            )
            count += 1
            
            # Marcar como publicado (al Saga processor)
            event.published_at = __import__("django.utils.timezone", fromlist=["now"]).now()
            event.save(update_fields=["published_at"])
    
    return {"processed": count}


@shared_task(name="retry_failed_transactions")
def retry_failed_transactions():
    """
    Reintenta transacciones que fallaron pero son recuperables.
    Se ejecuta periódicamente para manejar fallos transitorios.
    """
    from transactions.models import Transaction
    from django.utils import timezone
    from datetime import timedelta
    
    # Buscar transacciones fallidas hace menos de 1 hora
    failed_recent = Transaction.objects.filter(
        status=Transaction.Status.FAILED,
        saga_step=Transaction.SagaStep.FAILED,
        updated_at__gte=timezone.now() - timedelta(hours=1),
        reason__icontains="Debit failed"  # Solo reintentar debit failures
    )[:50]
    
    count = 0
    for tx in failed_recent:
        # Resetear estado a PENDING para reintentar
        tx.status = Transaction.Status.PENDING
        tx.saga_step = Transaction.SagaStep.PENDING
        tx.debit_idempotency_key = None  # Reset para nuevo intento
        tx.credit_idempotency_key = None
        tx.save()
        
        # Disparar saga nuevamente
        process_transaction_saga.apply_async(
            args=[str(tx.id)],
            countdown=5  # Esperar 5 segundos
        )
        count += 1
    
    return {"retried": count}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
