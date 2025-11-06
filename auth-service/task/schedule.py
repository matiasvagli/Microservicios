# task/schedule.py
from .celery import celery

# 🔹 Definir tareas automáticas
celery.conf.beat_schedule = {
    "reenviar-eventos-cada-5-min": {
        "task": "resend_pending_events",  # nombre definido en el decorador shared_task
        "schedule": 300.0,  # cada 300 segundos = 5 minutos
    },
}

print("Scheduler de tareas configurado.")