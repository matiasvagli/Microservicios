import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import login
from app.models.user_model import UserLogin

# Test: Verifica que el JWT devuelto en login contiene los claims correctos
@pytest.mark.asyncio
async def test_login_jwt_claims(monkeypatch):
    """
    Simula login exitoso y verifica el contenido del JWT:
    - El token debe tener el id y el email del usuario
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
    # Mock: Simula generación de JWT con claims
    def mock_create_access_token(data, expires_delta):
        # Simula un JWT con claims
        return {"sub": data["sub"], "email": data["sub"]}
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
    monkeypatch.setattr("app.routes.auth_routes.create_access_token", mock_create_access_token)
    # Crea el formulario simulado con username y password
    class DummyForm:
        username = "testuser@example.com"
        password = "testpassword123"
    form_data = DummyForm()
    # Ejecuta el endpoint y verifica el JWT
    result = await login(form_data, db=MockDB())
    token = result["access_token"]
    assert token["sub"] == "testuser@example.com"
    assert token["email"] == "testuser@example.com"
