# core/proxies/wallet_proxy.py
from fastapi import APIRouter, Request
import httpx

router = APIRouter(prefix="/wallet", tags=["Wallet"])
WALLET_SERVICE_URL = "http://wallet-service:8002"

@router.post("/create")
async def create_wallet(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{WALLET_SERVICE_URL}/wallet/create", json=await request.json())
    return response.json()

@router.get("/{user_id}")
async def get_wallet(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{WALLET_SERVICE_URL}/wallet/{user_id}")
    return response.json()
