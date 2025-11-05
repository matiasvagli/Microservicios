from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 🔹 MongoDB
    MONGO_URI: str = "mongodb://mongo:27017"
    DATABASE_NAME: str = "auth_db"

    # 🔹 JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 🔹 RabbitMQ (para cuando lo uses)
    RABBITMQ_HOST: Optional[str] = "rabbitmq"
    RABBITMQ_PORT: Optional[int] = 5672
    RABBITMQ_USER: Optional[str] = "guest"
    RABBITMQ_PASS: Optional[str] = "guest"
    RABBITMQ_QUEUE: Optional[str] = "user_registered"

    class Config:
        env_file = ".env"

settings = Settings()
