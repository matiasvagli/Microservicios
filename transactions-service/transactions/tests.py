from django.test import TestCase, Client
from django.urls import reverse
from .models import Transaction
import json


class TransactionAPITestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.url = "/api/transactions/transfer"

	def test_transfer_creates_transaction(self):
		payload = {
			"idempotency_key": "test123",
			"payer_user_id": "user_a",
			"payee_user_id": "user_b",
			"amount": "10.00",
			"currency": "ars",
		}
		response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertIn("id", data)
		tx = Transaction.objects.get(id=data["id"]) if isinstance(data, dict) else Transaction.objects.first()
		self.assertIsNotNone(tx)
		self.assertEqual(tx.payer_user_id, "user_a")
		self.assertEqual(tx.payee_user_id, "user_b")
		self.assertEqual(str(tx.amount), "10.00")

	def test_transfer_idempotency(self):
		payload = {
			"idempotency_key": "idem-456",
			"payer_user_id": "user_a",
			"payee_user_id": "user_b",
			"amount": "5.00",
			"currency": "ars",
		}
		r1 = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")
		r2 = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")
		self.assertEqual(r1.status_code, 200)
		self.assertEqual(r2.status_code, 200)
		id1 = r1.json().get("id") if isinstance(r1.json(), dict) else None
		id2 = r2.json().get("id") if isinstance(r2.json(), dict) else None
		# If endpoint returns the created transaction, they should be equal
		if id1 and id2:
			self.assertEqual(id1, id2)
		# Alternatively only one Transaction record exists
		self.assertEqual(Transaction.objects.filter(idempotency_key="idem-456").count(), 1)

	def test_outbox_created_on_transfer(self):
		payload = {
			"idempotency_key": "outbox-1",
			"payer_user_id": "user_a",
			"payee_user_id": "user_b",
			"amount": "7.00",
			"currency": "ars",
		}
		r = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")
		self.assertEqual(r.status_code, 200)
		# There should be an outbox event for transaction.created
		from .models import Outbox
		evs = Outbox.objects.filter(topic="transaction.created")
		self.assertTrue(evs.exists())
		# verify payload content of the latest event
		payload = evs.first().payload
		self.assertEqual(payload.get("idempotency_key"), "outbox-1")

