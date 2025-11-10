import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import login
from app.models.user_model import UserLogin

# Test: Verifica que al loguear se publica el evento para crear billetera
@pytest.mark.asyncio
async def test_login_event_wallet(monkeypatch):
    """
    Simula login exitoso y verifica que se publica el evento de creación de billetera
    """
    # Mock: Simula usuario existente
    async def mock_find_one(self, query):
        return {
            "_id": "user123",
            "email": query["email"],
            "full_name": "Test User",
            "hashed_password": "hash"
        }
    # Mock: Simula verificación de contraseña
    def mock_verify_password(plain, hashed):
        return True
    # Mock: Simula publicación de evento y verifica que se llama correctamente
    called = {"event": None, "payload": None}
    def mock_publish_event(event, payload, queue=None):
        called["event"] = event
        called["payload"] = payload
        return True
    # Mock: Simula la colección de refresh_tokens
    class MockRefreshTokens:
        async def update_one(self, query, update, upsert=False):
            return None
    # MockDB: Simula la base de datos
    class MockDB:
        users = type("Users", (), {
            "find_one": mock_find_one
        })()
        refresh_tokens = MockRefreshTokens()
    # Aplica los mocks
    monkeypatch.setattr("app.routes.auth_routes.verify_password", mock_verify_password)
    monkeypatch.setattr("app.routes.auth_routes.publish_event", mock_publish_event)
    # Crea el formulario simulado con username y password
    class DummyForm:
        username = "testuser@example.com"
        password = "testpassword123"
    form_data = DummyForm()
    # Ejecuta el endpoint
    await login(form_data, db=MockDB())
    # Verifica que se publicó el evento correcto
    assert called["event"] is not None
    assert called["event"] == "create_wallet"
    assert called["payload"]["user_id"] == "user123"
