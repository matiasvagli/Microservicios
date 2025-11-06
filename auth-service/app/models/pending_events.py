
from datetime import datetime
from pydantic import BaseModel, Field
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017")
db = client["auth_db"]
collection = db["failed_events"]

#clase para eventos pendientes pydantic para validación
class PendingEvent(BaseModel):
    event_type: str = Field(..., description="Tipo de evento (ej: user_created)")
    payload: dict = Field(..., description="Datos del evento")
    error: str = Field(..., description="Mensaje de error o excepción")
    status: str = Field(default="pending")
    retry_count: int = Field(default=0)
    last_retry: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

#función para guardar eventos pendientes
def save_pending_event(event_type: str, payload: dict, error: str):
    """Guarda un evento fallido en la base."""
    event = PendingEvent(event_type=event_type, payload=payload, error=error)
    collection.insert_one(event.model_dump())
    print(f"[⚠️] Evento pendiente guardado: {event_type}")
