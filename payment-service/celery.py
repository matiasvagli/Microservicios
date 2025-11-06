from celery import Celery
from datetime import timedelta

# Importa la tarea de reintentos
from task.resend_failed_payments import resend_failed_payments

celery = Celery('payment_tasks')

celery.conf.update(
    broker_url='amqp://guest:guest@rabbitmq:5672//',
    result_backend='rpc://',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
    timezone='America/Argentina/Buenos_Aires',
    beat_schedule={
        'reenviar-pagos-cada-1-min': {
            'task': 'resend_failed_payments',
            'schedule': timedelta(minutes=1),
        },
    },
)
