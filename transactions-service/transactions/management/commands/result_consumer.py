from django.core.management.base import BaseCommand
import os
import json
import pika
from transactions.models import Transaction, Outbox
from django.db import transaction as db_transaction

class Command(BaseCommand):
    help = 'Escuchar resultados de transacciones desde el wallet-service y actualizar estados'

    def handle(self, *args, **options):
        host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        queue_name = 'transaction.results'

        self.stdout.write(f"[*] Conectando a RabbitMQ en {host}...")
        
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)

            def callback(ch, method, properties, body):
                self.stdout.write(f" [<-] Resultado recibido: {body}")
                data = json.loads(body)
                tx_id = data.get("transaction_id")
                status = data.get("status")
                error_msg = data.get("error")

                try:
                    with db_transaction.atomic():
                        tx = Transaction.objects.filter(id=tx_id).first()
                        if tx:
                            if status == "COMPLETED":
                                tx.status = Transaction.Status.COMPLETED
                            else:
                                tx.status = Transaction.Status.FAILED
                            tx.save()
                            
                            self.stdout.write(self.style.SUCCESS(f" [OK] TX {tx_id} actualizada a {tx.status}"))
                        else:
                            self.stdout.write(self.style.WARNING(f" [!] TX {tx_id} no encontrada"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f" [!] Error actualizando TX: {e}"))

                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=queue_name, on_message_callback=callback)
            self.stdout.write(self.style.SUCCESS(f"[*] Escuchando en {queue_name}. CTRL+C para salir"))
            channel.start_consuming()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f" [!] Error de conexión: {e}"))
