from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None  # 👈 opcional, por si querés devolver ambos
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class RefreshTokenData(BaseModel):
    email: EmailStr
    token: str  # 👈 minúscula por convención (antes tenías "Token")
    updated_at: datetime = datetime.utcnow()
