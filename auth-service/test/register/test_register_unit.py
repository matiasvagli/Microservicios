import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from app.routes.auth_routes import register
from app.models.user_model import UserCreate

# Test: Verifica que el endpoint /register registra correctamente un usuario nuevo
@pytest.mark.asyncio
async def test_register_user_unit(monkeypatch):
    # Mock: Simula que la base de datos NO encuentra el usuario (usuario nuevo)
    async def mock_find_one(self, query):
        return None

    # Mock: Simula la inserción de usuario en la base de datos
    class MockInsertResult:
        inserted_id = "fakeid123"
    async def mock_insert_one(self, data):
        return MockInsertResult()

    # Mock: Simula la publicación de eventos (RabbitMQ)
    def mock_publish_event(event, payload, queue=None):
        return True

    # MockDB: Simula el objeto de base de datos con los métodos mockeados
    class MockDB:
        users = type("Users", (), {
            "find_one": mock_find_one,
            "insert_one": mock_insert_one
        })()

    # Aplica el mock de publicación de eventos
    monkeypatch.setattr("app.routes.auth_routes.publish_event", mock_publish_event)

    # Crea el usuario de prueba
    user = UserCreate(email="testuser@example.com", full_name="Test User", password="testpassword123")

    # Ejecuta el endpoint como función y verifica el resultado
    result = await register(user, db=MockDB())
    assert result.email == "testuser@example.com"
    assert result.id == "fakeid123"
    assert result.is_active is True
