from django.core.management.base import BaseCommand
import os
import json
from transactions.models import Outbox
from datetime import datetime

try:
    import pika
except Exception:
    pika = None


class Command(BaseCommand):
    help = 'Publicar eventos pendientes desde la tabla Outbox a RabbitMQ'

    def handle(self, *args, **options):
        unsent = Outbox.objects.filter(published_at__isnull=True)
        self.stdout.write(f"Eventos pendientes: {unsent.count()}")
        for ev in unsent:
            try:
                body = json.dumps(ev.payload)
                self.publish(ev.topic, body)
                ev.published_at = datetime.utcnow()
                ev.save()
                self.stdout.write(self.style.SUCCESS(f"Publicado: {ev.topic} ({ev.id})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Fallo al publicar {ev.id}: {e}"))

    def publish(self, topic: str, body: str):
        if pika is None:
            print("pika no está instalado. Simulando publicación...")
            print(f"Publish -> {topic}: {body}")
            return

        host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        port = int(os.getenv('RABBITMQ_PORT', '5672'))
        user = os.getenv('RABBITMQ_USER', 'guest')
        password = os.getenv('RABBITMQ_PASS', 'guest')
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=topic, durable=True)
        channel.basic_publish(exchange='', routing_key=topic, body=body)
        connection.close()
