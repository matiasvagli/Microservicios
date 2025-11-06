import json
import pika
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "payment_events")

def publish_payment_confirmed(user_id: str, amount: float, currency: str):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    event = {
        "event": "payment.confirmed",
        "user_id": user_id,
        "amount": amount,
        "currency": currency,
    }

    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print(f"📤 Evento enviado: {event}")
    connection.close()
