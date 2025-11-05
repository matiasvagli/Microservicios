import os, sys, django, pika, json, time
from django.utils import timezone

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallet_service.settings")
django.setup()

from wallets.models import Wallet

print("Iniciando consumer...")

def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            channel = connection.channel()
            channel.queue_declare(queue="user_registered", durable=True)
            print("Conectado a RabbitMQ — esperando mensajes...")

            def callback(ch, method, properties, body):
                print(f"Mensaje recibido: {body}")
                data = json.loads(body)
                user_id = data.get("user_id")

                wallet, created = Wallet.objects.get_or_create(
                    user_id=user_id,
                    defaults={
                        "account_number": f"ACCT-{user_id[-6:].upper()}",
                        "balance": 0,
                        "currency": "ARS",
                        "created_at": timezone.now(),
                    },
                )
                if created:
                    print(f"Wallet creada para usuario {user_id}")
                else:
                    print(f"Wallet ya existía para usuario {user_id}")

            channel.basic_consume(queue="user_registered", on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except Exception as e:
            print(f"Error al conectar/consumir RabbitMQ: {e}")
            print("Reintentando en 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
