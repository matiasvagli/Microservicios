from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user_model import UserCreate, UserResponse, Token
from app.db.connection import get_database
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RefreshRequest(BaseModel):
    refresh_token: str


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type = payload.get("type")

        if email is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception

    return user


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    user_dict.pop("password")

    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return UserResponse(**user_dict)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": user["email"]}, access_token_expires)
    refresh_token = create_refresh_token({"sub": user["email"]})

    # Guardamos el refresh token (rotación)
    await db.refresh_tokens.update_one(
        {"email": user["email"]},
        {"$set": {"token": refresh_token, "updated_at": datetime.utcnow()}},
        upsert=True
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token/refresh", response_model=Token)
async def refresh_token(data: RefreshRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        refresh_token = data.refresh_token # Obtener el refresh token del cuerpo de la solicitud
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        saved = await db.refresh_tokens.find_one({"email": email})
        if not saved or saved["token"] != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid or rotated token")

        new_access_token = create_access_token({"sub": email})
        new_refresh_token = create_refresh_token({"sub": email})

        # Rotamos el refresh token (reemplazamos el anterior)
        await db.refresh_tokens.update_one(
            {"email": email},
            {"$set": {"token": new_refresh_token, "updated_at": datetime.utcnow()}}
        )

        return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
