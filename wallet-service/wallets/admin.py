
from django.contrib import admin
from .models import Wallet, Transaction

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'account_number', 'balance', 'currency', 'created_at', 'updated_at')
    search_fields = ('user_id', 'account_number')
    list_filter = ('currency', 'created_at')

admin.site.register(Wallet, WalletAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'wallet', 'amount', 'transaction_type', 'description', 'created_at')
    search_fields = ('transaction_id', 'wallet__account_number', 'wallet__user_id')
    list_filter = ('transaction_type', 'created_at')

admin.site.register(Transaction, TransactionAdmin)