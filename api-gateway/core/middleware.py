
# api-gateway/core/middleware.py trabajamos la seguridad de las peticiones


from fastapi import Request # Importante para manejar las solicitudes HTTP
from fastapi.responses import JSONResponse # Importante para manejar las respuestas HTTP
from starlette.middleware.base import BaseHTTPMiddleware # Importante para crear middleware personalizado
import jwt
import os

# Preferir la clave desde la variable de entorno si está disponible
SECRET_KEY = os.getenv("SECRET_KEY", "CLAVE12345")  # Clave secreta para firmar los tokens JWT
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Algoritmo de firma para los tokens JWT

# Middleware para validar JWT en las solicitudes entrantes
class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rutas públicas (no requieren token)
        public_paths = ["/auth/login", "/auth/register", "/"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Leer encabezado Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Token requerido"})

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # Si querés, podés agregar request.state.user = payload["sub"]
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Token expirado"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail": "Token inválido"})

        # Si el token es válido, continúa al siguiente middleware o ruta
        response = await call_next(request)
        return response