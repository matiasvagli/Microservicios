from django.db import models
import uuid
from django.utils import timezone

# Create your models here.
#modelo de dominio para las transacciones
class Transaction(models.Model):
    class Status(models.TextChoices):#clase anidada para los estados de la transacción
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.CharField(max_length=64, unique=True)
    payer_user_id = models.CharField(max_length=100)
    payee_user_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=10, default="ars")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reason = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["payer_user_id"]),
            models.Index(fields=["payee_user_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.payer_user_id} → {self.payee_user_id} | {self.amount} {self.currency} | {self.status}"
    
#modelo para la tabla outbox que guarda eventos pendientes de publicar
class Outbox(models.Model):
    """
    Guarda eventos pendientes de enviar a RabbitMQ.
    Cada fila representa un mensaje a publicar.
    """

    id = models.BigAutoField(primary_key=True)
    topic = models.CharField(max_length=100)  # ej: "transaction.completed"
    payload = models.JSONField()              # datos del evento
    created_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["topic"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        status = "✅" if self.published_at else "⏳"
        return f"{status} {self.topic} @ {self.created_at:%Y-%m-%d %H:%M:%S}"    