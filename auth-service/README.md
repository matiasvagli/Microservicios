
# Auth Service — Microservicio de autenticación (FastAPI + MongoDB)

Servicio de autenticación que provee registro de usuarios, login con JWTs, refresh/rotación de tokens y endpoints protegidos. Diseñado para integrarse con un API Gateway en un entorno de microservicios.

## Endpoints principales
- `POST /register`
	- Registra un usuario (JSON):
		```json
		{
			"email": "demo@example.com",
			"full_name": "Usuario Demo",
			"password": "ClaveSegura123"
		}
		```

- `POST /token`
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

- `POST /token/refresh`
	- Envía `{ "refresh_token": "..." }` y devuelve nuevos tokens (rotación segura).

- `GET /users/me`
	- Devuelve datos del usuario autenticado. Header: `Authorization: Bearer <access_token>`

## Documentación interactiva
- Swagger UI: [`/docs`](http://localhost:8000/docs)
- Redoc: [`/redoc`](http://localhost:8000/redoc)

## Seguridad
- Contraseñas hasheadas con bcrypt (passlib).
- Tokens firmados con `SECRET_KEY` y expiración configurable.
- Validación explícita de tipo de token (access vs refresh) y rotación de refresh tokens.

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
- `user_registered`: Se publica al registrar un usuario
- Otros eventos según la lógica del sistema

## Autor
Matias Vagliviello

Te dejo el archivo `.env.example` listo para copiar y pegar como `.env` en la raíz del servicio para pruebas locales.

---
Para dudas o mejoras, abre un issue o contactactame.
