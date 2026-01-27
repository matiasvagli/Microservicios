"""
Saga Orchestrator para transacciones distribuidas.
Coordina debit/credit entre wallets con compensación automática.
"""
import os
import requests
import uuid
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from .models import Transaction, Outbox


class WalletServiceClient:
    """Cliente HTTP para comunicarse con Wallet Service"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("WALLET_SERVICE_URL", "http://wallet-service:8001")
    
    def debit(self, user_id: str, amount: Decimal, idempotency_key: str) -> dict:
        """Intenta debitar de la wallet del usuario"""
        try:
            response = requests.post(
                f"{self.base_url}/api/wallets/{user_id}/debit",
                json={
                    "amount": str(amount),
                    "idempotency_key": idempotency_key
                },
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def credit(self, user_id: str, amount: Decimal, idempotency_key: str) -> dict:
        """Acredita a la wallet del usuario"""
        try:
            response = requests.post(
                f"{self.base_url}/api/wallets/{user_id}/credit",
                json={
                    "amount": str(amount),
                    "idempotency_key": idempotency_key
                },
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}


class TransactionSaga:
    """Orquesta la saga de transferencia de dinero entre wallets"""
    
    def __init__(self, wallet_client: WalletServiceClient = None):
        self.wallet_client = wallet_client or WalletServiceClient()
    
    def execute(self, transaction_id: str) -> dict:
        """
        Ejecuta la saga completa:
        1. Validar transaction existe y está en PENDING
        2. Debitar del payer
        3. Acreditar al payee
        4. Si ambos éxito → COMPLETED
        5. Si falla en credit → COMPENSATE (reverso del debit) → FAILED
        """
        try:
            # Fetch transaction
            tx = Transaction.objects.get(id=transaction_id)
            
            if tx.status != Transaction.Status.PENDING:
                return {"success": False, "error": f"Transaction not in PENDING state: {tx.status}"}
            
            # Step 1: DEBIT PAYER
            tx.saga_step = Transaction.SagaStep.DEBITING
            tx.save(update_fields=["saga_step", "updated_at"])
            
            debit_key = tx.debit_idempotency_key or f"debit-{tx.id}"
            tx.debit_idempotency_key = debit_key
            tx.save(update_fields=["debit_idempotency_key"])
            
            debit_result = self.wallet_client.debit(
                user_id=tx.payer_user_id,
                amount=tx.amount,
                idempotency_key=debit_key
            )
            
            if not debit_result["success"]:
                # Debit falló, no compensar
                tx.status = Transaction.Status.FAILED
                tx.saga_step = Transaction.SagaStep.FAILED
                tx.reason = f"Debit failed: {debit_result['error']}"
                tx.save(update_fields=["status", "saga_step", "reason", "updated_at"])
                
                self._publish_event(
                    tx,
                    "transaction.failed",
                    {"error": debit_result['error'], "step": "DEBITING"}
                )
                return {"success": False, "error": debit_result['error'], "step": "DEBITING"}
            
            # Step 2: CREDIT PAYEE
            tx.saga_step = Transaction.SagaStep.CREDITING
            tx.save(update_fields=["saga_step", "updated_at"])
            
            credit_key = tx.credit_idempotency_key or f"credit-{tx.id}"
            tx.credit_idempotency_key = credit_key
            tx.save(update_fields=["credit_idempotency_key"])
            
            credit_result = self.wallet_client.credit(
                user_id=tx.payee_user_id,
                amount=tx.amount,
                idempotency_key=credit_key
            )
            
            if not credit_result["success"]:
                # Credit falló → COMPENSATE: reversar el debit
                tx.saga_step = Transaction.SagaStep.COMPENSATING
                tx.save(update_fields=["saga_step", "updated_at"])
                
                compensation_key = f"compensation-{tx.id}"
                compensation_result = self.wallet_client.credit(
                    user_id=tx.payer_user_id,
                    amount=tx.amount,
                    idempotency_key=compensation_key
                )
                
                if compensation_result["success"]:
                    tx.status = Transaction.Status.FAILED
                    tx.saga_step = Transaction.SagaStep.FAILED
                    tx.reason = f"Credit failed: {credit_result['error']}. Debit reversed."
                    tx.save(update_fields=["status", "saga_step", "reason", "updated_at"])
                    
                    self._publish_event(
                        tx,
                        "transaction.failed_compensated",
                        {
                            "error": credit_result['error'],
                            "step": "CREDITING",
                            "compensation": "debit_reversed"
                        }
                    )
                    return {"success": False, "error": credit_result['error'], "compensated": True}
                else:
                    # Compensación falló → estado crítico
                    tx.status = Transaction.Status.FAILED
                    tx.saga_step = Transaction.SagaStep.FAILED
                    tx.reason = f"Credit failed AND compensation failed: {compensation_result['error']}"
                    tx.save(update_fields=["status", "saga_step", "reason", "updated_at"])
                    
                    self._publish_event(
                        tx,
                        "transaction.critical_failure",
                        {
                            "error": credit_result['error'],
                            "compensation_error": compensation_result['error'],
                            "needs_manual_review": True
                        }
                    )
                    return {"success": False, "error": "Credit failed and compensation failed", "critical": True}
            
            # ✅ SUCCESS: Both debit and credit succeeded
            tx.status = Transaction.Status.COMPLETED
            tx.saga_step = Transaction.SagaStep.COMPLETED
            tx.save(update_fields=["status", "saga_step", "updated_at"])
            
            self._publish_event(
                tx,
                "transaction.completed",
                {
                    "payer_balance": debit_result['data'].get('new_balance'),
                    "payee_balance": credit_result['data'].get('new_balance')
                }
            )
            return {"success": True, "message": "Transaction completed successfully"}
        
        except Transaction.DoesNotExist:
            return {"success": False, "error": f"Transaction {transaction_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _publish_event(self, tx: Transaction, topic: str, payload: dict = None):
        """Publica evento al outbox"""
        base_payload = {
            "transaction_id": str(tx.id),
            "idempotency_key": tx.idempotency_key,
            "payer_user_id": tx.payer_user_id,
            "payee_user_id": tx.payee_user_id,
            "amount": str(tx.amount),
            "currency": tx.currency,
            "status": tx.status,
        }
        if payload:
            base_payload.update(payload)
        
        Outbox.objects.create(topic=topic, payload=base_payload)
