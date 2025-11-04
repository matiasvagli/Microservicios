🧑‍💻 Microservicio de Usuarios
📄 Descripción general

Servicio encargado del registro, autenticación y gestión de usuarios.
Implementado con FastAPI, MongoDB y autenticación mediante JWT.
Se comunica con otros servicios (como billetera o transferencias) a través del API Gateway.

🧱 Tecnologías principales

FastAPI (framework web)

MongoDB (base de datos NoSQL)

Motor async: motor

bcrypt (hash de contraseñas)

python-jose (generación y validación de JWT)

Pydantic (validaciones de entrada/salida)

Docker Compose (orquestación de contenedores)

⚙️ Estructura del proyecto
auth-service/
 ├── app/
 │   ├── main.py
 │   ├── core/
 │   │   ├── config.py        # Variables de entorno, conexión Mongo
 │   │   └── security.py      # Funciones JWT / bcrypt
 │   ├── models/
 │   │   └── user_model.py    # Definición del modelo de usuario (Pydantic + Mongo)
 │   ├── routes/
 │   │   └── user_routes.py   # Endpoints: register, login, profile
 │   └── db/
 │       └── connection.py    # Conexión Mongo con motor
 ├── Dockerfile
 ├── requirements.txt
 └── .env

🧩 Endpoints principales
Método	Ruta	Descripción	Autenticación
POST	/auth/register	Registro de nuevo usuario	❌
POST	/auth/login	Login y generación de token JWT	❌
GET	/users/me	Perfil del usuario logueado	✅ (Bearer Token)
GET	/users/all	Listar todos los usuarios (admin)	✅
🔐 Ejemplo de autenticación JWT
Login

Request:

{
  "email": "usuario@test.com",
  "password": "123456"
}


Response:

{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}

Header de autorización
Authorization: Bearer <jwt_token>

🧠 Flujo interno

El usuario se registra → se hashea la contraseña con bcrypt

Al hacer login → se valida el hash y se genera un JWT

Cada request autenticado se valida con un dependency que decodifica el JWT

Si es válido → se obtiene el user_id del token para usarlo en otras consultas


## 🧰 Variables de entorno (.env)

| Variable | Descripción | Ejemplo |
|-----------|-------------|----------|
| `MONGO_URI` | URL de conexión a MongoDB | `mongodb://mongo_users:27017` |
| `MONGO_DB` | Nombre de la base de datos | `usuarios_db` |
| `JWT_SECRET_KEY` | Clave secreta para firmar tokens | `super_secret_key` |
| `JWT_ALGORITHM` | Algoritmo de firma del JWT | `HS256` |
| `JWT_EXPIRE_MINUTES` | Tiempo de expiración del token | `60` |
