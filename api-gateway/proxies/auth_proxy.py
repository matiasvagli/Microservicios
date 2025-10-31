# core/proxies/auth_proxy.py
from fastapi import APIRouter, Request
import httpx

router = APIRouter(prefix="/auth", tags=["Auth"])
AUTH_SERVICE_URL = "http://auth-service:8001"

@router.post("/register")
async def register_user(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=await request.json())
    return response.json()

@router.post("/login")
async def login_user(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/login", json=await request.json())
    return response.json()
