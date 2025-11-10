import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import login
from app.models.user_model import UserLogin

# Test: Login válido, usuario y contraseña correctos
@pytest.mark.asyncio
async def test_login_valid(monkeypatch):
    """
    Simula un login exitoso:
    - El usuario existe en la base de datos
    - La contraseña es correcta
    - Se publica el evento de creación de billetera
    - Se devuelve un JWT válido
    """
    # Mock: Simula usuario existente con hash correcto
    async def mock_find_one(self, query):
        return {
            "_id": "user123",
            "email": query["email"],
            "full_name": "Test User",
            "hashed_password": "$2b$12$saltsaltsaltsaltsaltsaltsaltsalt1234567890123456789012345678901234567890" # bcrypt hash
        }
    # Mock: Simula verificación de contraseña
    def mock_verify_password(plain, hashed):
        return True
    # Mock: Simula publicación de evento (éxito)
    def mock_publish_event(event, payload, queue=None):
        return True
    # Mock: Simula generación de JWT
    def mock_create_access_token(data, expires_delta):
        return "jwt.token.simulado"
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
    monkeypatch.setattr("app.routes.auth_routes.create_access_token", mock_create_access_token)
    # Crea el formulario simulado con username y password
    class DummyForm:
        username = "testuser@example.com"
        password = "testpassword123"
    form_data = DummyForm()
    # Ejecuta el endpoint y verifica el resultado
    result = await login(form_data, db=MockDB())
    assert result["access_token"] == "jwt.token.simulado"
    assert result["token_type"] == "bearer"
    # Aquí podrías verificar que el evento de billetera se publicó correctamente
