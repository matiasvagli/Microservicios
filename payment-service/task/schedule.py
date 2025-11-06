# task/schedule.py
from .celery import celery

# 🔹 Definir tareas automáticas
celery.conf.beat_schedule = {
    "reenviar-pagos-cada-1-min": {
        "task": "resend_failed_payments",  # nombre definido en el decorador shared_task
        "schedule": 60.0,  # cada 60 segundos = 1 minuto
    },
}

print("Scheduler de tareas de pagos configurado.")
