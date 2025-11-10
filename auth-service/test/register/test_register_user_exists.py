import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import register
from app.models.user_model import UserCreate
from fastapi import HTTPException

# Test: Verifica que el endpoint /register devuelve error si el usuario ya existe
@pytest.mark.asyncio
async def test_register_user_exists(monkeypatch):
    # Mock: Simula que la base de datos encuentra un usuario con el mismo email
    async def mock_find_one(self, query):
        # Devuelve un diccionario simulando el usuario existente
        return {"email": query["email"]}

    # Mock: Si intenta insertar, lanza excepción (no debería llegar aquí)
    async def mock_insert_one(self, data):
        raise Exception("No debería intentar insertar si el usuario existe")

    # Mock: Simula la publicación de eventos (no relevante en este test)
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

    # Espera que el endpoint lance una excepción HTTP 400 por usuario existente
    with pytest.raises(HTTPException) as exc_info:
        await register(user, db=MockDB())
    # Verifica el código y mensaje de error
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"
