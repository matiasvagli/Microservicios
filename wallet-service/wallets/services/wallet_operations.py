"""
Servicio para manejar operaciones de wallet (debit/credit) con idempotencia
"""
from decimal import Decimal
from django.db import transaction, IntegrityError
from wallets.models import Wallet, Transaction as WalletTransaction


class WalletOperationService:
    """Servicio para operaciones de wallet con idempotencia"""
    
    @staticmethod
    def debit(user_id: str, amount: Decimal, idempotency_key: str) -> dict:
        """
        Debita de una wallet (retira dinero).
        
        Retorna:
        - success: bool
        - new_balance: Decimal (si éxito)
        - error: str (si error)
        """
        try:
            with transaction.atomic():
                # Obtener o crear wallet
                wallet, _ = Wallet.objects.get_or_create(
                    user_id=user_id,
                    defaults={"balance": Decimal("0.00")}
                )
                
                # Verificar idempotencia: si ya existe tx con esta key, retornar
                existing_tx = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="DEBIT",
                    description__icontains=idempotency_key
                ).first()
                
                if existing_tx:
                    return {
                        "success": True,
                        "new_balance": wallet.balance,
                        "message": "Debit already processed (idempotent)"
                    }
                
                # Validar saldo disponible
                if wallet.balance < amount:
                    return {
                        "success": False,
                        "error": "Insufficient balance",
                        "current_balance": wallet.balance
                    }
                
                # Realizar debit
                wallet.balance -= amount
                wallet.save()
                
                # Registrar transacción
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type="DEBIT",
                    description=f"Debit via saga: {idempotency_key}"
                )
                
                return {
                    "success": True,
                    "new_balance": wallet.balance,
                    "message": "Debit successful"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def credit(user_id: str, amount: Decimal, idempotency_key: str) -> dict:
        """
        Acredita a una wallet (deposita dinero).
        
        Retorna:
        - success: bool
        - new_balance: Decimal (si éxito)
        - error: str (si error)
        """
        try:
            with transaction.atomic():
                # Obtener o crear wallet
                wallet, _ = Wallet.objects.get_or_create(
                    user_id=user_id,
                    defaults={"balance": Decimal("0.00")}
                )
                
                # Verificar idempotencia
                existing_tx = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type="CREDIT",
                    description__icontains=idempotency_key
                ).first()
                
                if existing_tx:
                    return {
                        "success": True,
                        "new_balance": wallet.balance,
                        "message": "Credit already processed (idempotent)"
                    }
                
                # Realizar credit
                wallet.balance += amount
                wallet.save()
                
                # Registrar transacción
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type="CREDIT",
                    description=f"Credit via saga: {idempotency_key}"
                )
                
                return {
                    "success": True,
                    "new_balance": wallet.balance,
                    "message": "Credit successful"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
