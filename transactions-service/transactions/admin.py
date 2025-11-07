from django.contrib import admin
from .models import Transaction
# Register your models here.

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "payer_user_id", "payee_user_id", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("payer_user_id", "payee_user_id", "idempotency_key")


from .models import Outbox

@admin.register(Outbox)
class OutboxAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "created_at", "published_at")
    list_filter = ("topic",)
    search_fields = ("topic",)

