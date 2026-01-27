"""
Tests para operaciones de Wallet (Debit/Credit)
"""
from django.test import TestCase, Client
from decimal import Decimal
import json
from wallets.models import Wallet
from wallets.services.wallet_operations import WalletOperationService


class WalletOperationServiceTestCase(TestCase):
    """Tests para WalletOperationService"""
    
    def setUp(self):
        self.service = WalletOperationService()
    
    def test_debit_success(self):
        """Test: Debit exitoso"""
        # Create wallet
        wallet = Wallet.objects.create(
            user_id="user_a",
            balance=Decimal("1000.00")
        )
        
        # Debit
        result = self.service.debit(
            user_id="user_a",
            amount=Decimal("100.00"),
            idempotency_key="debit-001"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['new_balance'], Decimal("900.00"))
        
        # Verify in DB
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("900.00"))
    
    def test_debit_insufficient_balance(self):
        """Test: Debit falla por falta de saldo"""
        wallet = Wallet.objects.create(
            user_id="user_b",
            balance=Decimal("50.00")
        )
        
        result = self.service.debit(
            user_id="user_b",
            amount=Decimal("100.00"),
            idempotency_key="debit-002"
        )
        
        self.assertFalse(result['success'])
        self.assertIn("Insufficient", result['error'])
        
        # Balance no cambia
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("50.00"))
    
    def test_debit_idempotency(self):
        """Test: Debit idempotent (misma key retorna mismo resultado)"""
        wallet = Wallet.objects.create(
            user_id="user_c",
            balance=Decimal("500.00")
        )
        
        # Primera llamada
        result1 = self.service.debit(
            user_id="user_c",
            amount=Decimal("100.00"),
            idempotency_key="debit-idem-001"
        )
        
        # Segunda llamada con misma key
        result2 = self.service.debit(
            user_id="user_c",
            amount=Decimal("100.00"),
            idempotency_key="debit-idem-001"
        )
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertEqual(result1['new_balance'], Decimal("400.00"))
        self.assertEqual(result2['new_balance'], Decimal("400.00"))
        
        # Solo una transacción en DB
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("400.00"))
        from wallets.models import Transaction
        debits = Transaction.objects.filter(
            wallet=wallet,
            transaction_type="DEBIT"
        )
        self.assertEqual(debits.count(), 1)
    
    def test_credit_success(self):
        """Test: Credit exitoso"""
        wallet = Wallet.objects.create(
            user_id="user_d",
            balance=Decimal("100.00")
        )
        
        result = self.service.credit(
            user_id="user_d",
            amount=Decimal("50.00"),
            idempotency_key="credit-001"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['new_balance'], Decimal("150.00"))
        
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("150.00"))
    
    def test_credit_creates_wallet_if_not_exists(self):
        """Test: Credit crea wallet si no existe"""
        result = self.service.credit(
            user_id="user_new",
            amount=Decimal("100.00"),
            idempotency_key="credit-new"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['new_balance'], Decimal("100.00"))
        
        wallet = Wallet.objects.get(user_id="user_new")
        self.assertEqual(wallet.balance, Decimal("100.00"))
    
    def test_credit_idempotency(self):
        """Test: Credit idempotent"""
        wallet = Wallet.objects.create(
            user_id="user_e",
            balance=Decimal("200.00")
        )
        
        result1 = self.service.credit(
            user_id="user_e",
            amount=Decimal("50.00"),
            idempotency_key="credit-idem-001"
        )
        
        result2 = self.service.credit(
            user_id="user_e",
            amount=Decimal("50.00"),
            idempotency_key="credit-idem-001"
        )
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertEqual(result1['new_balance'], Decimal("250.00"))
        self.assertEqual(result2['new_balance'], Decimal("250.00"))
        
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("250.00"))


class WalletAPITestCase(TestCase):
    """Tests para endpoints de Wallet API"""
    
    def setUp(self):
        self.client = Client()
    
    def test_debit_endpoint(self):
        """Test: Endpoint POST /wallets/{user_id}/debit"""
        wallet = Wallet.objects.create(
            user_id="user_api",
            balance=Decimal("1000.00")
        )
        
        response = self.client.post(
            "/api/wallets/user_api/debit",
            data=json.dumps({
                "amount": "100.00",
                "idempotency_key": "api-debit-001"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(str(data['new_balance']), "900.00")
    
    def test_credit_endpoint(self):
        """Test: Endpoint POST /wallets/{user_id}/credit"""
        wallet = Wallet.objects.create(
            user_id="user_api2",
            balance=Decimal("500.00")
        )
        
        response = self.client.post(
            "/api/wallets/user_api2/credit",
            data=json.dumps({
                "amount": "250.00",
                "idempotency_key": "api-credit-001"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(str(data['new_balance']), "750.00")
    
    def test_debit_missing_idempotency_key(self):
        """Test: Debit sin idempotency_key retorna error"""
        response = self.client.post(
            "/api/wallets/user_test/debit",
            data=json.dumps({"amount": "100.00"}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("idempotency_key", data.get('error', ''))
