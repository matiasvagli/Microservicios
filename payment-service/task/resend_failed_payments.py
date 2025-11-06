from celery import shared_task
from db.mongo import failed_payments
from services.rabbitmq import publish_payment_confirmed
from datetime import datetime

@shared_task(name='resend_failed_payments')
def resend_failed_payments():
    """
    Reintenta enviar eventos de pago pendientes guardados en MongoDB.
    """
    print("[🔍] Buscando pagos pendientes en MongoDB...")
    pending = list(failed_payments.find({
        "status": "pending",
        "retry_count": {"$lt": 5}
    }))
    print(f"[📊] Pagos pendientes por reintentar: {len(pending)}")
    for event in pending:
        try:
            publish_payment_confirmed(**event["payload"])
            failed_payments.delete_one({"_id": event["_id"]})
            print(f"[✅] Pago reenviado exitosamente para usuario {event['payload']['user_id']} (event_id: {event['_id']})")
        except Exception as e:
            failed_payments.update_one(
                {"_id": event["_id"]},
                {
                    "$inc": {"retry_count": 1},
                    "$set": {
                        "last_retry": datetime.utcnow(),
                        "last_error": str(e),
                        "status": "failed" if event.get("retry_count", 0) >= 4 else "pending"
                    }
                }
            )
            print(f"[x] Error reenviando {event['_id']}: {e}")
            print(f"[⚠️] Reintento {event.get('retry_count', 0) + 1}/5")
