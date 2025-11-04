from django.db import models
from django.utils import timezone
import uuid

class Wallet(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    account_number = models.CharField(max_length=20, unique=True, default="")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default="ARS")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            # Genera un número de cuenta único al crearla
            self.account_number = f"ACCT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Wallet({self.account_number}) - User {self.user_id} - ${self.balance}"



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
    ]

    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} on {self.wallet.account_number}"
