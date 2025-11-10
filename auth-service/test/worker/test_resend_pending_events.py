import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from task.resend_pending import resend_pending_events

# Test: Verifica que el worker elimina el evento pendiente si la publicación es exitosa
@pytest.mark.asyncio
async def test_resend_pending_events_success(monkeypatch):
    # MockCollection simula la colección de eventos pendientes en MongoDB
    class MockCollection:
        def find(self, query=None):
            # Devuelve una lista con un solo evento pendiente
            return [{
                "_id": "evt123",
                "event_type": "user_registered",
                "payload": {"user_id": "user123"},
                "status": "pending",
                "retry_count": 0
            }]
        def delete_one(self, query):
            # Marca que se eliminó el evento (para verificar en el test)
            self.deleted = True
            return None
        def update_one(self, query, update):
            # Marca que se actualizó el evento (no debería ocurrir en este test)
            self.updated = True
            return None
    # Mockea la colección de eventos fallidos
    monkeypatch.setattr("task.resend_pending.failed_events", MockCollection())
    # Mockea la función de publicación para que no falle (simula éxito)
    def mock_publish_event(event_type, payload, queue=None):
        return True
    monkeypatch.setattr("task.resend_pending.publish_event", mock_publish_event)
    # Ejecuta el worker (procesa los eventos)
    resend_pending_events()
    # Importa el mock directamente del módulo y verifica que fue eliminado
    from task.resend_pending import failed_events
    assert failed_events.deleted

# Test: Verifica que el worker actualiza el evento si la publicación falla
@pytest.mark.asyncio
async def test_resend_pending_events_fail(monkeypatch):
    # MockCollection simula la colección de eventos pendientes en MongoDB
    class MockCollection:
        def find(self, query=None):
            # Devuelve una lista con un solo evento pendiente
            return [{
                "_id": "evt123",
                "event_type": "user_registered",
                "payload": {"user_id": "user123"},
                "status": "pending",
                "retry_count": 0
            }]
        def delete_one(self, query):
            # Marca que NO se eliminó el evento (para verificar en el test)
            self.deleted = False
            return None
        def update_one(self, query, update):
            # Marca que se actualizó el evento (para verificar en el test)
            self.updated = True
            return None
    # Mockea la colección de eventos fallidos
    monkeypatch.setattr("task.resend_pending.failed_events", MockCollection())
    # Mockea la función de publicación para que falle (simula error en RabbitMQ)
    def mock_publish_event(event_type, payload, queue=None):
        raise Exception("RabbitMQ no disponible")
    monkeypatch.setattr("task.resend_pending.publish_event", mock_publish_event)
    # Ejecuta el worker (procesa los eventos)
    resend_pending_events()
    # Importa el mock directamente del módulo y verifica que fue actualizado
    from task.resend_pending import failed_events
    assert failed_events.updated
