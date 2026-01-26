import os
import sys
import json
import pika
import django
import traceback
from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone

# Configuración de Django
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallet_service.settings")
django.setup()

from wallets.models import Wallet, Transaction

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_IN = "transaction.created"
QUEUE_OUT = "transaction.results"

def publish_result(result_payload):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_OUT, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_OUT,
            body=json.dumps(result_payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        print(f" [x] Resultado publicado: {result_payload['status']} para TX {result_payload['transaction_id']}")
    except Exception as e:
        print(f" [!] Error al publicar resultado: {e}")

def process_transaction(body):
    data = json.loads(body)
    tx_id = data.get("transaction_id")
    payer_id = data.get("payer_user_id")
    payee_id = data.get("payee_user_id")
    amount = Decimal(data.get("amount"))
    
    print(f" [->] Procesando TX {tx_id}: {payer_id} -> {payee_id} (${amount})")

    result_status = "FAILED"
    error_msg = ""

    try:
        with db_transaction.atomic():
            # Obtener wallets con select_for_update para evitar condiciones de carrera
            payer_wallet = Wallet.objects.select_for_update().filter(user_id=payer_id).first()
            payee_wallet = Wallet.objects.select_for_update().filter(user_id=payee_id).first()

            if not payer_wallet:
                raise ValueError(f"Wallet de origen no encontrada ({payer_id})")
            if not payee_wallet:
                raise ValueError(f"Wallet de destino no encontrada ({payee_id})")
            if payer_wallet.balance < amount:
                raise ValueError("Saldo insuficiente")

            # Ejecutar débitos y créditos
            payer_wallet.balance -= amount
            payer_wallet.save()
            
            payee_wallet.balance += amount
            payee_wallet.save()

            # Registrar transacciones locales
            Transaction.objects.create(
                wallet=payer_wallet,
                amount=-amount,
                transaction_type="DEBIT",
                description=f"Transferencia enviada a {payee_id} (TX: {tx_id})",
                created_at=timezone.now()
            )
            Transaction.objects.create(
                wallet=payee_wallet,
                amount=amount,
                transaction_type="CREDIT",
                description=f"Transferencia recibida de {payer_id} (TX: {tx_id})",
                created_at=timezone.now()
            )
            
            result_status = "COMPLETED"
            print(f" [OK] TX {tx_id} completada exitosamente")

    except Exception as e:
        result_status = "FAILED"
        error_msg = str(e)
        print(f" [!] TX {tx_id} falló: {error_msg}")

    # Publicar resultado de vuelta al transactions-service
    publish_result({
        "transaction_id": tx_id,
        "status": result_status,
        "error": error_msg
    })

def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_IN, durable=True)
            
            def callback(ch, method, properties, body):
                process_transaction(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_IN, on_message_callback=callback)
            
            print(f" [*] Escuchando en {QUEUE_IN}. Para salir presiona CTRL+C")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print(" [!] Error de conexión con RabbitMQ, reintentando en 5s...")
            import time
            time.sleep(5)
        except Exception as e:
            print(f" [!] Error inesperado: {e}")
            traceback.print_exc()
            import time
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
