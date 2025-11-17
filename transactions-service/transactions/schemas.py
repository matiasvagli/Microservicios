from ninja import Schema
from typing import Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class TransactionCreate(Schema):
    idempotency_key: str
    payer_user_id: str
    payee_user_id: str
    amount: Decimal
    currency: Optional[str] = "ars"
    reason: Optional[str] = ""


class TransactionOut(Schema):
    id: UUID
    idempotency_key: str
    payer_user_id: str
    payee_user_id: str
    amount: Decimal
    currency: str
    status: str
    reason: str
    created_at: datetime
    updated_at: datetime


class StatusUpdate(Schema):
    status: str
