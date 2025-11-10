
# Auth Service — Microservicio de autenticación (FastAPI + MongoDB)

Servicio de autenticación que provee registro de usuarios, login con JWTs, refresh/rotación de tokens y endpoints protegidos. Diseñado para integrarse con un API Gateway en un entorno de microservicios.

## Endpoints principales
	- Registra un usuario (JSON):
		```json
		{
			"email": "demo@example.com",
			"full_name": "Usuario Demo",
			"password": "ClaveSegura123"
		}
		```

	- Autentica y devuelve access + refresh token. Enviar como `application/x-www-form-urlencoded`:
		- username: demo@example.com
		- password: ClaveSegura123
	- Respuesta (ejemplo):
		```json
		{
			"access_token": "jwt_access_token...",
			"refresh_token": "jwt_refresh_token...",
			"token_type": "bearer"
		}
		```

	- Envía `{ "refresh_token": "..." }` y devuelve nuevos tokens (rotación segura).

	- Devuelve datos del usuario autenticado. Header: `Authorization: Bearer <access_token>`

## Documentación interactiva

## Seguridad

## Variables de entorno (.env)
Configurar en la raíz del servicio (`auth-service/.env`):

```
MONGO_URI=mongodb://mongo:27017
DATABASE_NAME=auth_db
SECRET_KEY=super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Instalación y ejecución
```bash
# Instalar dependencias
poetry install

# Ejecutar el servicio
poetry run uvicorn main:app --reload
```

## Testing
```bash
poetry run pytest --maxfail=3 --disable-warnings -v
```

## Docker Compose
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

## Estructura principal
```
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
```

## Eventos publicados

## Autor
Matias Vagliviello

Te dejo el archivo `.env.example` listo para copiar y pegar como `.env` en la raíz del servicio para pruebas locales.

Para dudas o mejoras, abre un issue o contactactame.

# Auth Service - Microservicios

##  Descripción
Servicio de autenticación y autorización para arquitectura de microservicios: registro, login (JWT), validación de credenciales y publicación de eventos para integración con otros servicios.

Forma parte del ecosistema:
- Auth Service (este)
- Wallet Service
- Transactions Service
- API Gateway

## Tecnologías usadas
- Python 3.x
- FastAPI (ASGI framework)
- Pydantic para validación de datos
- Motor/MongoDB
- JWT para autenticación
- Celery/RabbitMQ (eventos)
- Pytest / pytest-asyncio / httpx para testing

##  Configuración & desarrollo
### Requisitos
- Python ≥ 3.xx
- MongoDB corriendo localmente o vía contenedor
- Variables de entorno definidas (ver abajo)

### Variables de entorno
Configura en la raíz del servicio (`auth-service/.env`). Ejemplo:
```env
SECRET_KEY=tu_super_secreto
MONGO_URL=mongodb://localhost:27017/authdb
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EVENT_BROKER_URL=amqp://guest:guest@localhost:5672/
```
Te lo dejo listo podes  copiar `.env.example` y renombrarlo a `.env` para pruebas locales.

##  Endpoints principales
Método | Ruta | Descripción
--- | --- | ---
POST | /auth/register | Registra un nuevo usuario
POST | /auth/token | Autentica usuario y devuelve token JWT
POST | /auth/token/refresh | Rotación segura de refresh token
GET | /auth/users/me | Devuelve información del usuario validado

### Ejemplo de petición para registro
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@ejemplo.com","full_name":"Usuario Ejemplo","password":"secret"}'
```
### Ejemplo de respuesta
```json
{
  "id": "60f5a3b2c8d1b1b2f4c2d6e7",
  "email": "usuario@ejemplo.com",
  "full_name": "Usuario Ejemplo",
  "is_active": true
}
```

## 🧪 Testing
Tests unitarios mockean la base de datos y dependencias externas (eventos, hashing).
Tests de integración prueban la API real con la base de datos de testing.
```bash
pytest tests/unit --maxfail=1 --disable-warnings -q
pytest tests/integration
```

## Documentación interactiva
- Swagger UI: [`/docs`](http://localhost:8000/docs)
- Redoc: [`/redoc`](http://localhost:8000/redoc)

##  Seguridad
- Contraseñas hasheadas con bcrypt (passlib)
- Tokens firmados con `SECRET_KEY` y expiración configurable
- Validación de tipo de token y rotación de refresh tokens

##  Docker Compose
El servicio puede ejecutarse con Docker Compose:
```bash
docker compose up -d mongo
docker compose build auth-service
docker compose up auth-service
```

##  Estructura principal
```
app/
  ├─ core/
  │   ├─ config.py        # Configuración y carga de .env
  │   └─ security.py      # Hashing, generación y verificación de tokens
  ├─ db/
  │   └─ connection.py    # Conexión asíncrona a MongoDB (Motor)
  ├─ models/
  │   └─ user_model.py    # Schemas Pydantic
  ├─ routes/
  │   └─ auth_routes.py   # Endpoints de autenticación
  └─ main.py              # Punto de entrada FastAPI
```

## Eventos publicados
- `user_registered`: Se publica al registrar un usuario
- Otros eventos según la lógica del sistema



## 👤 Autor
Matias Vagliviello

---
Para dudas, mejoras o soporte, abre un issue o contactactame.
