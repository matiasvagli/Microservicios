from celery import Celery
from datetime import timedelta

# Importar tareas primero
from .resend_pending import resend_pending_events

# Crear instancia de Celery
celery = Celery('auth_tasks')

# Configuración básica
celery.conf.update(
    # Broker y backend
    broker_url='amqp://guest:guest@rabbitmq:5672//',
    result_backend='rpc://',
    
    # Configuración de broker
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        'client_properties': {
            'connection_name': 'auth-service-celery'
        }
    },
    
    # Configuración de colas
    task_default_queue='auth_service_tasks',
    task_queues={
        'auth_service_tasks': {
            'exchange': 'auth_service',
            'routing_key': 'auth_service.tasks',
        },
    },
    task_default_exchange='auth_service',
    task_default_routing_key='auth_service.tasks',
    
    # Serialización
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone y UTC
    enable_utc=True,
    timezone='America/Argentina/Buenos_Aires',
    
    # Beat Schedule
    beat_schedule={
        'reenviar-eventos-cada-5-min': {
            'task': 'resend_pending_events',
            'schedule': timedelta(seconds=30),  # Temporalmente cada 30 segundos para pruebas
        },
    },
)