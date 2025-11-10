import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import refresh_token, RefreshRequest
from fastapi import HTTPException

# Test: Refresh token inválido (tipo incorrecto)
@pytest.mark.asyncio
async def test_token_refresh_type_invalid(monkeypatch):
    """
    Simula un refresh token con tipo incorrecto:
    - El token tiene tipo 'access' en vez de 'refresh'
    - Debe lanzar HTTPException 401
    """
    def mock_jwt_decode(token, secret, algorithms):
        return {"sub": "testuser@example.com", "type": "access"}
    class MockDB:
        class MockRefreshTokens:
            async def find_one(self, query):
                return {"email": "testuser@example.com", "token": "valid_refresh_token"}
            async def update_one(self, query, update):
                return None
        refresh_tokens = MockRefreshTokens()
    monkeypatch.setattr("app.routes.auth_routes.jwt.decode", mock_jwt_decode)
    data = RefreshRequest(refresh_token="valid_refresh_token")
    with pytest.raises(HTTPException) as exc_info:
        await refresh_token(data, db=MockDB())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type"

# Test: Refresh token inválido (token no coincide)
@pytest.mark.asyncio
async def test_token_refresh_rotated(monkeypatch):
    """
    Simula un refresh token que no coincide con el guardado (rotado):
    - Debe lanzar HTTPException 401
    """
    def mock_jwt_decode(token, secret, algorithms):
        return {"sub": "testuser@example.com", "type": "refresh"}
    class MockDB:
        class MockRefreshTokens:
            async def find_one(self, query):
                return {"email": "testuser@example.com", "token": "other_token"}
            async def update_one(self, query, update):
                return None
        refresh_tokens = MockRefreshTokens()
    monkeypatch.setattr("app.routes.auth_routes.jwt.decode", mock_jwt_decode)
    data = RefreshRequest(refresh_token="valid_refresh_token")
    with pytest.raises(HTTPException) as exc_info:
        await refresh_token(data, db=MockDB())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or rotated token"

# Test: Refresh token inválido (JWTError)
@pytest.mark.asyncio
async def test_token_refresh_jwt_error(monkeypatch):
    """
    Simula error al decodificar el JWT
    - Debe lanzar HTTPException 401
    """
    from jose import JWTError
    def mock_jwt_decode(token, secret, algorithms):
        raise JWTError("JWTError")
    class MockDB:
        class MockRefreshTokens:
            async def find_one(self, query):
                return {"email": "testuser@example.com", "token": "valid_refresh_token"}
            async def update_one(self, query, update):
                return None
        refresh_tokens = MockRefreshTokens()
    monkeypatch.setattr("app.routes.auth_routes.jwt.decode", mock_jwt_decode)
    data = RefreshRequest(refresh_token="valid_refresh_token")
    with pytest.raises(HTTPException) as exc_info:
        await refresh_token(data, db=MockDB())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid refresh token"
