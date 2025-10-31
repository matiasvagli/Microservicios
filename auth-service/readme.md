Auth Service — Microservicio de autenticación (FastAPI + MongoDB)

Descripción
-----------
Servicio de autenticación que provee registro de usuarios, login con JWTs, refresh/rotación de tokens y endpoints protegidos. Diseñado para integrarse con un API Gateway en un entorno de microservicios.

Estructura principal
-------------------
app/
  ├─ core/
  │   ├─ config.py        # Configuración y carga de .env
  │   └─ security.py      # Hashing, generación y verificación de tokens
  ├─ db/
  │   └─ connection.py    # Conexión asíncrona a MongoDB (Motor)
  ├─ models/
  │   └─ user_model.py    # Schemas Pydantic (UserCreate, UserResponse, Token, ...)
  ├─ routes/
  │   └─ auth_routes.py   # Endpoints de autenticación
  └─ main.py              # Punto de entrada FastAPI

Principales endpoints
----------------------
- POST /auth/register
  - Registra un usuario (JSON):
    {
      "email": "demo@example.com",
      "full_name": "Usuario Demo",
      "password": "ClaveSegura123"
    }

- POST /auth/token
  - Autentica y devuelve access + refresh token. Enviar como `application/x-www-form-urlencoded`:
    - username: demo@example.com
    - password: ClaveSegura123

  Respuesta (ejemplo):
    {
      "access_token": "jwt_access_token...",
      "refresh_token": "jwt_refresh_token...",
      "token_type": "bearer"
    }

- POST /auth/token/refresh
  - Envía { "refresh_token": "..." } y devuelve nuevos tokens (rotación segura).

- GET /auth/users/me
  - Devuelve datos del usuario autenticado. Header: `Authorization: Bearer <access_token>`

Seguridad
---------
- Contraseñas hasheadas con bcrypt (passlib).
- Tokens firmados con `SECRET_KEY` y expiración configurable.
- Validación explícita de tipo de token (access vs refresh) y rotación de refresh tokens.

Variables de entorno (.env)
-------------------------
Configurar en la raíz del servicio (`auth-service/.env`):

MONGO_URI=mongodb://mongo:27017
DATABASE_NAME=auth_db
SECRET_KEY=super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Docker (rápido)
---------------
El servicio puede ejecutarse con Docker Compose (desde la raíz del repo):

1) Levantar solo dependencias (opcional):

```bash
docker compose up -d mongo
```

2) Construir y levantar el servicio:

```bash
docker compose build auth-service
docker compose up auth-service
```

Acceder a la documentación interactiva de FastAPI:

http://localhost:8001/docs

Testing rápido
-------------
1) Registrar usuario: POST /auth/register (JSON)
2) Obtener token: POST /auth/token (x-www-form-urlencoded)
3) Usar `Authorization: Bearer <access_token>` para endpoints protegidos

Notas
-----
Este proyecto es ideal para un portfolio de microservicios. El Auth Service expone tokens JWT que pueden ser validados por un API Gateway para proteger otros servicios (wallet, transactions, etc.).

Autor
-----
Matías Vagliviello — Proyecto educativo / portfolio
