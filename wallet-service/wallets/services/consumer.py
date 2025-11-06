import os, sys, django, pika, json, time, traceback
from django.utils import timezone

print("🔄 Configurando entorno...")
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallet_service.settings")
try:
    print("🔄 Inicializando Django...")
    django.setup()
    print("✅ Django inicializado correctamente")
except Exception as e:
    print(f"❌ Error al inicializar Django: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("🔄 Importando modelo Wallet...")
    from wallets.models import Wallet
    print("✅ Modelo Wallet importado correctamente")
except Exception as e:
    print(f"❌ Error al importar modelo Wallet: {e}")
    traceback.print_exc()
    sys.exit(1)

print("🚀 Iniciando consumer...")

def start_consumer():
    while True:
        try:
            print("🔄 Intentando conectar a RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host="rabbitmq",
                connection_attempts=5,
                retry_delay=5,
                client_properties={'connection_name': 'wallet-service-consumer'}
            ))
            channel = connection.channel()
            print("✅ Conexión a RabbitMQ establecida")
            
            # Cola para eventos en tiempo real
            print("🔄 Declarando cola user_events...")
            channel.queue_declare(queue="user_events", durable=True)
            print("✅ Cola user_events declarada")
            
            # Cola para eventos reintentados
            print("🔄 Declarando cola pending_events...")
            channel.queue_declare(queue="pending_events", durable=True)
            print("✅ Cola pending_events declarada")
            
            print("🔌 Conectado a RabbitMQ — esperando mensajes...")

            def callback(ch, method, properties, body):
                print(f"Mensaje recibido: {body}")
                data = json.loads(body)
                # Soportar ambos formatos: caliente y reintento
                if "payload" in data and isinstance(data["payload"], dict):
                    user_id = data["payload"].get("user_id")
                else:
                    user_id = data.get("user_id")

                if not user_id:
                    print(f"[⚠️] No se encontró user_id en el mensaje: {data}")
                    return

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

            # Consumir de ambas colas
            channel.basic_consume(queue="user_events", on_message_callback=callback, auto_ack=True)
            channel.basic_consume(queue="pending_events", on_message_callback=callback, auto_ack=True)
            
            print("👂 Escuchando colas: user_events, pending_events")
            channel.start_consuming()
        except Exception as e:
            print(f"Error al conectar/consumir RabbitMQ: {e}")
            print("Reintentando en 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        print("🔄 Iniciando proceso principal del consumer...")
        start_consumer()
    except Exception as e:
        print(f"❌ Error fatal en el consumer: {e}")
        traceback.print_exc()
        sys.exit(1)
