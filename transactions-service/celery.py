"""
Celery app configuration for transactions-service
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transactions_service.settings")

app = Celery("transactions_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Consumir eventos de transaction.created cada 10 segundos
    "consume-transaction-events": {
        "task": "tasks.saga_tasks.consume_transaction_events",
        "schedule": 10.0,  # 10 segundos
    },
    # Reintentar transacciones fallidas cada 5 minutos
    "retry-failed-transactions": {
        "task": "tasks.saga_tasks.retry_failed_transactions",
        "schedule": crontab(minute="*/5"),  # Cada 5 minutos
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
