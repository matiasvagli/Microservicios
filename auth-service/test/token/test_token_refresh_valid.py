import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import refresh_token, RefreshRequest
from fastapi import HTTPException

# Test: Refresh token válido, devuelve nuevos tokens
@pytest.mark.asyncio
async def test_token_refresh_valid(monkeypatch):
    """
    Simula un refresh token válido:
    - El token tiene tipo 'refresh'
    - El token coincide con el guardado en la base
    - Devuelve nuevos tokens
    """
    # Mock: Simula decodificación JWT válida
    def mock_jwt_decode(token, secret, algorithms):
        return {"sub": "testuser@example.com", "type": "refresh"}
    # Mock: Simula búsqueda del token en la base
    async def mock_find_one(query):
        return {"email": "testuser@example.com", "token": "valid_refresh_token"}
    # Mock: Simula actualización del token
    async def mock_update_one(query, update):
        return None
    # Mock: Simula generación de nuevos tokens
    def mock_create_access_token(data):
        return "new_access_token"
    def mock_create_refresh_token(data):
        return "new_refresh_token"
    # MockDB: Simula la base de datos
    class MockRefreshTokens:
        async def find_one(self, query):
            return await mock_find_one(query)
        async def update_one(self, query, update):
            return await mock_update_one(query, update)
    class MockDB:
        refresh_tokens = MockRefreshTokens()
    # Aplica los mocks
    monkeypatch.setattr("app.routes.auth_routes.jwt.decode", mock_jwt_decode)
    monkeypatch.setattr("app.routes.auth_routes.create_access_token", mock_create_access_token)
    monkeypatch.setattr("app.routes.auth_routes.create_refresh_token", mock_create_refresh_token)
    # Ejecuta el endpoint y verifica el resultado
    data = RefreshRequest(refresh_token="valid_refresh_token")
    result = await refresh_token(data, db=MockDB())
    assert result["access_token"] == "new_access_token"
    assert result["refresh_token"] == "new_refresh_token"
    assert result["token_type"] == "bearer"
