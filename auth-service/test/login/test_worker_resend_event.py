import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from task.resend_pending import resend_pending_events

# Test: El worker reintenta publicar el evento pendiente de billetera
@pytest.mark.asyncio
async def test_worker_resend_event(monkeypatch):
    """
    Simula que el worker encuentra un evento pendiente y lo publica correctamente
    """
    # MockCollection: Simula la colección de eventos pendientes
    class MockCollection:
        def find(self, query=None):
            return [{
                "_id": "evt_wallet",
                "event_type": "create_wallet",
                "payload": {"user_id": "user123"},
                "status": "pending",
                "retry_count": 0
            }]
        def delete_one(self, query):
            self.deleted = True
            return None
        def update_one(self, query, update):
            self.updated = True
            return None
    # Mockea la colección de eventos fallidos
    monkeypatch.setattr("task.resend_pending.failed_events", MockCollection())
    # Mockea la función de publicación para que no falle
    def mock_publish_event(event_type, payload, queue=None):
        return True
    monkeypatch.setattr("task.resend_pending.publish_event", mock_publish_event)
    # Ejecuta el worker
    resend_pending_events()
    # Verifica que el evento fue eliminado correctamente
    from task.resend_pending import failed_events
    assert failed_events.deleted
