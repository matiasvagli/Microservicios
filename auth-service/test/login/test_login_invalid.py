import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from app.routes.auth_routes import login
from app.models.user_model import UserLogin
from fastapi import HTTPException

# Test: Login inválido, usuario no existe o contraseña incorrecta
@pytest.mark.asyncio
async def test_login_invalid(monkeypatch):
    """
    Simula un login fallido:
    - El usuario no existe en la base de datos
    - O la contraseña es incorrecta
    - Debe devolver error 401
    """
    # Mock: Simula usuario no encontrado
    async def mock_find_one(self, query):
        return None
    # Mock: Simula verificación de contraseña (no relevante si usuario no existe)
    def mock_verify_password(plain, hashed):
        return False
    # MockDB: Simula la base de datos
    class MockDB:
        users = type("Users", (), {
            "find_one": mock_find_one
        })()
    # Aplica los mocks
    monkeypatch.setattr("app.routes.auth_routes.verify_password", mock_verify_password)
    # Crea el formulario simulado con username y password
    class DummyForm:
        username = "nouser@example.com"
        password = "wrongpassword"
    form_data = DummyForm()
    # Espera que el endpoint lance una excepción HTTP 401
    with pytest.raises(HTTPException) as exc_info:
        await login(form_data, db=MockDB())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect username or password"
