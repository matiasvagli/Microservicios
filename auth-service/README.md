
# Auth Service - Microservicio de autenticación (FastAPI + MongoDB)

Servicio de autenticación y autorización para arquitectura de microservicios: registro, login (JWT), validación de credenciales y publicación de eventos para integración con otros servicios.

## Ecosistema
| Servicio         | Rol principal                |
|------------------|-----------------------------|
| Auth Service     | Autenticación y eventos     |
| Wallet Service   | Gestión de billeteras       |
| Transactions     | Movimientos y transferencias|
| API Gateway      | Orquestación y routing      |

## Tecnologías
**Python 3.x**, **FastAPI**, **Pydantic**, **MongoDB/Motor**, **JWT**, **Celery/RabbitMQ**, **Pytest**

## Configuración
**Requisitos:** Python ≥ 3.xx, MongoDB local/contenedor, variables de entorno.

**Variables de entorno (`.env`):**
```env
SECRET_KEY=tu_super_secreto
MONGO_URL=mongodb://localhost:27017/authdb
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EVENT_BROKER_URL=amqp://guest:guest@localhost:5672/
```
Te dejo el example listo, podés copiar y pegar `.env.example` y renombrarlo a `.env` para pruebas locales.

## Endpoints principales
| Método | Ruta                  | Descripción                       |
|--------|-----------------------|-----------------------------------|
| POST   | /auth/register        | Registra un nuevo usuario         |
| POST   | /auth/token           | Autentica y devuelve JWT          |
| POST   | /auth/token/refresh   | Rotación segura de refresh token  |
| GET    | /auth/users/me        | Info del usuario autenticado      |

### Ejemplo de registro
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@ejemplo.com","full_name":"Usuario Ejemplo","password":"secret"}'
```
**Respuesta:**
```json
{
  "id": "60f5a3b2c8d1b1b2f4c2d6e7",
  "email": "usuario@ejemplo.com",
  "full_name": "Usuario Ejemplo",
  "is_active": true
}
```

### Ejemplo de login
```bash
curl -X POST http://localhost:8001/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@ejemplo.com&password=secret"
```
**Respuesta:**
```json
{
  "access_token": "jwt_access_token...",
  "refresh_token": "jwt_refresh_token...",
  "token_type": "bearer"
}
```

## Testing
Tests unitarios mockean la base de datos y dependencias externas (eventos, hashing).
Tests de integración prueban la API real con la base de datos de testing.
```bash
pytest tests/unit --maxfail=1 --disable-warnings -q
pytest tests/integration
```

## Documentación interactiva
- [Swagger UI](http://localhost:8000/docs)
- [Redoc](http://localhost:8000/redoc)

## Seguridad
- Contraseñas hasheadas con bcrypt (passlib)
- Tokens firmados con `SECRET_KEY` y expiración configurable
- Validación de tipo de token y rotación de refresh tokens

## Docker Compose
```bash
docker compose up -d mongo
docker compose build auth-service
docker compose up auth-service
```

## Estructura
```text
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

## Autor
Matias Vagliviello

---
Para dudas, mejoras o soporte, abre un issue o contactactame.