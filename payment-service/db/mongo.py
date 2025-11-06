from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("PAYMENT_DB_NAME", "payment_db")
COLLECTION_NAME = os.getenv("FAILED_PAYMENTS_COLLECTION", "failed_payments")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
failed_payments = db[COLLECTION_NAME]

def save_failed_payment(event_type, payload, error=None):
    doc = {
        "event_type": event_type,
        "payload": payload,
        "status": "pending",
        "retry_count": 0,
        "last_error": error,
    }
    result = failed_payments.insert_one(doc)
    return result.inserted_id

# Puedes agregar más helpers aquí para buscar, actualizar o eliminar eventos
