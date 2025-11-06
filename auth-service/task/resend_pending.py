# task/resend_pending.py
from celery import shared_task
from pymongo import MongoClient
from datetime import datetime
from app.services.events import publish_event

# 🔹 Conexión a Mongo
client = MongoClient(
    "mongodb://mongo:27017",
    appname="auth-service-retry-worker"
)
db = client["auth_db"]
failed_events = db["failed_events"]

@shared_task(name='resend_pending_events')
def resend_pending_events():
    """Reintenta enviar eventos pendientes guardados en MongoDB."""
    print("[🔍] Buscando eventos pendientes en MongoDB...")
    
    # Buscar todos los eventos primero para debug
    all_events = list(failed_events.find({}))
    print(f"[📊] Total de eventos en la colección: {len(all_events)}")
    for evt in all_events:
        print(f"[📝] Evento encontrado: {evt}")
    
    # Buscar eventos pendientes con menos de 5 reintentos
    pending = list(failed_events.find({
        "status": "pending",
        "retry_count": {"$lt": 5}
    }))
    print(f"[📊] Eventos pendientes por reintentar: {len(pending)}")
    
    for event in pending:
        try:
            # Publicar en la cola de eventos pendientes
            publish_event(event["event_type"], event["payload"], queue="pending_events")
            # Si el evento se envía correctamente, lo eliminamos
            failed_events.delete_one({"_id": event["_id"]})
            print(f"[✅] Evento reenviado exitosamente para usuario {event['payload']['user_id']} (event_id: {event['_id']})")
        except Exception as e:
            # Incrementar contador de reintentos y actualizar último intento
            failed_events.update_one(
                {"_id": event["_id"]},
                {
                    "$inc": {"retry_count": 1},
                    "$set": {
                        "last_retry": datetime.utcnow(),
                        "error": str(e),
                        "status": "failed" if event.get("retry_count", 0) >= 4 else "pending"
                    }
                }
            )
            print(f"[x] Error reenviando {event['_id']}: {e}")
            print(f"[⚠️] Reintento {event.get('retry_count', 0) + 1}/5")