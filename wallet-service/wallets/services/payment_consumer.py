import json
import pika
import os
import django
import sys
from decimal import Decimal
from django.utils import timezone

# ================================
# Configuración inicial de Django
# ================================
sys.path.append("/app")  # ruta raíz del proyecto Django dentro del contenedor
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallet_service.settings")
django.setup()

from wallets.models import Wallet, Transaction

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE_PAYMENTS", "payment_events")



def process_payment(event):
    """
    Procesa un evento payment.confirmed:
    Actualiza saldo de la wallet y crea una transacción.
    """
    user_id = event["user_id"]
    amount = Decimal(event["amount"])
    currency = event.get("currency", "ARS")

    wallet = Wallet.objects.filter(user_id=user_id).first()
    if not wallet:
        print(f"⚠️ Wallet no encontrada para user_id={user_id}")
        return

    wallet.balance += amount
    wallet.save()

    Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type="CREDIT",
        description="Depósito confirmado",
        created_at=timezone.now(),
    )

    print(f"💰 Depósito procesado: +{amount} {currency} para {user_id}")


def consume_payments():
    """
    Escucha eventos de RabbitMQ y los procesa.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    def callback(ch, method, properties, body):
        event = json.loads(body)
        if event.get("event") == "payment.confirmed":
            process_payment(event)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    print("🎧 Esperando eventos de pago...")
    channel.start_consuming()


if __name__ == "__main__":
    consume_payments()
