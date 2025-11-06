# events.py
import pika, json
from app.models.pending_events import save_pending_event

def publish_event(event_type: str, payload: dict, queue: str = "user_events"):
    """Intenta publicar el evento. Si falla, lo guarda para reintento."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host="rabbitmq",
            client_properties={'connection_name': 'auth-service-publisher'}
        ))
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        message = json.dumps({"event_type": event_type, "payload": payload})
        channel.basic_publish(exchange="", routing_key=queue, body=message)
        connection.close()
        print(f"[✅] Evento enviado: {event_type}")
    except Exception as e:
        print(f"[x] Error al enviar evento: {e}")
        save_pending_event(event_type, payload, str(e))
        print(f"[⚠️] Evento guardado para reintento: {event_type}")