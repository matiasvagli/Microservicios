"""
Tests para Transaction Saga Pattern
"""
from django.test import TestCase
from unittest.mock import Mock, patch
from decimal import Decimal
from .models import Transaction, Outbox
from .saga_orchestrator import TransactionSaga, WalletServiceClient


class SagaOrchestratorTestCase(TestCase):
    """Tests para la Saga de transacciones"""

    def setUp(self):
        self.saga = TransactionSaga()
        # Mock del wallet client
        self.mock_wallet_client = Mock(spec=WalletServiceClient)
        self.saga.wallet_client = self.mock_wallet_client

    def test_saga_success_full_flow(self):
        """Test: Saga completa exitosa (debit + credit)"""
        # Create a transaction in PENDING state
        tx = Transaction.objects.create(
            idempotency_key="saga-test-1",
            payer_user_id="user_a",
            payee_user_id="user_b",
            amount=Decimal("100.00"),
            currency="ars",
            status=Transaction.Status.PENDING,
            saga_step=Transaction.SagaStep.PENDING,
        )

        # Mock: debit succeed
        self.mock_wallet_client.debit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("900.00")}
        }

        # Mock: credit succeed
        self.mock_wallet_client.credit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("1100.00")}
        }

        # Execute saga
        result = self.saga.execute(str(tx.id))

        # Assert result
        self.assertTrue(result["success"])

        # Reload transaction from DB
        tx.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.COMPLETED)
        self.assertEqual(tx.saga_step, Transaction.SagaStep.COMPLETED)

        # Assert outbox event published
        events = Outbox.objects.filter(topic="transaction.completed")
        self.assertTrue(events.exists())

    def test_saga_debit_fails(self):
        """Test: Falla el debit, sin compensación"""
        tx = Transaction.objects.create(
            idempotency_key="saga-test-debit-fail",
            payer_user_id="user_a",
            payee_user_id="user_b",
            amount=Decimal("100.00"),
            currency="ars",
            status=Transaction.Status.PENDING,
            saga_step=Transaction.SagaStep.PENDING,
        )

        # Mock: debit fail
        self.mock_wallet_client.debit.return_value = {
            "success": False,
            "error": "Insufficient balance"
        }

        # Execute saga
        result = self.saga.execute(str(tx.id))

        # Assert result
        self.assertFalse(result["success"])
        self.assertEqual(result["step"], "DEBITING")

        # Reload transaction
        tx.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.FAILED)
        self.assertIn("Debit failed", tx.reason)

        # Assert credit NOT called
        self.mock_wallet_client.credit.assert_not_called()

    def test_saga_credit_fails_compensation_succeeds(self):
        """Test: Credit falla pero compensación (reverso debit) exitosa"""
        tx = Transaction.objects.create(
            idempotency_key="saga-test-credit-fail",
            payer_user_id="user_a",
            payee_user_id="user_b",
            amount=Decimal("100.00"),
            currency="ars",
            status=Transaction.Status.PENDING,
            saga_step=Transaction.SagaStep.PENDING,
        )

        # Mock: debit succeed
        self.mock_wallet_client.debit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("900.00")}
        }

        # Mock: credit fail
        # Mock: compensation (credit back to payer) succeed
        self.mock_wallet_client.credit.side_effect = [
            {"success": False, "error": "Payee account not found"},  # credit fail
            {"success": True, "data": {"new_balance": Decimal("1000.00")}}  # compensation succeed
        ]

        # Execute saga
        result = self.saga.execute(str(tx.id))

        # Assert result
        self.assertFalse(result["success"])
        self.assertTrue(result.get("compensated"))

        # Reload transaction
        tx.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.FAILED)
        self.assertIn("reversed", tx.reason.lower())

        # Assert outbox event for compensated failure
        events = Outbox.objects.filter(topic="transaction.failed_compensated")
        self.assertTrue(events.exists())

    def test_saga_credit_fails_compensation_also_fails(self):
        """Test: Credit falla y compensación también falla = CRITICAL"""
        tx = Transaction.objects.create(
            idempotency_key="saga-test-critical",
            payer_user_id="user_a",
            payee_user_id="user_b",
            amount=Decimal("100.00"),
            currency="ars",
            status=Transaction.Status.PENDING,
            saga_step=Transaction.SagaStep.PENDING,
        )

        # Mock: debit succeed
        self.mock_wallet_client.debit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("900.00")}
        }

        # Mock: credit fail, compensation also fail
        self.mock_wallet_client.credit.side_effect = [
            {"success": False, "error": "Payee not found"},
            {"success": False, "error": "Service unavailable"}
        ]

        # Execute saga
        result = self.saga.execute(str(tx.id))

        # Assert result
        self.assertFalse(result["success"])
        self.assertTrue(result.get("critical"))

        # Reload transaction
        tx.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.FAILED)

        # Assert outbox event for critical failure
        events = Outbox.objects.filter(topic="transaction.critical_failure")
        self.assertTrue(events.exists())
        payload = events.first().payload
        self.assertTrue(payload.get("needs_manual_review"))

    def test_saga_transaction_not_found(self):
        """Test: Transacción no existe"""
        result = self.saga.execute("nonexistent-id")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    def test_saga_idempotency_debit_key(self):
        """Test: Debit idempotency key es consistente"""
        tx = Transaction.objects.create(
            idempotency_key="saga-idem-test",
            payer_user_id="user_a",
            payee_user_id="user_b",
            amount=Decimal("50.00"),
            currency="ars",
        )

        self.mock_wallet_client.debit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("950.00")}
        }

        self.mock_wallet_client.credit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("1050.00")}
        }

        # Execute saga
        self.saga.execute(str(tx.id))

        # Check that debit_idempotency_key fue asignado
        tx.refresh_from_db()
        self.assertIsNotNone(tx.debit_idempotency_key)
        self.assertIsNotNone(tx.credit_idempotency_key)

        # Verify que fue usado en las llamadas
        call_args = self.mock_wallet_client.debit.call_args
        self.assertEqual(
            call_args[1]["idempotency_key"],
            tx.debit_idempotency_key
        )

    def test_saga_step_transitions(self):
        """Test: Estados de saga_step progresan correctamente"""
        tx = Transaction.objects.create(
            idempotency_key="saga-step-test",
            payer_user_id="user_a",
            payee_user_id="user_b",
            amount=Decimal("75.00"),
            currency="ars",
            status=Transaction.Status.PENDING,
            saga_step=Transaction.SagaStep.PENDING,
        )

        self.mock_wallet_client.debit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("925.00")}
        }

        self.mock_wallet_client.credit.return_value = {
            "success": True,
            "data": {"new_balance": Decimal("1075.00")}
        }

        # Execute saga
        self.saga.execute(str(tx.id))

        # Verify final state
        tx.refresh_from_db()
        self.assertEqual(tx.saga_step, Transaction.SagaStep.COMPLETED)
