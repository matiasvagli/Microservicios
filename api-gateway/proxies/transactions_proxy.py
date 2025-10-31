# core/proxies/transactions_proxy.py
from fastapi import APIRouter, Request
import httpx

router = APIRouter(prefix="/transactions", tags=["Transactions"])
TRANSACTIONS_SERVICE_URL = "http://transactions-service:8003"

@router.post("/create")
async def create_transaction(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TRANSACTIONS_SERVICE_URL}/transactions/create", json=await request.json())
    return response.json()

@router.get("/{wallet_id}")
async def get_transactions(wallet_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TRANSACTIONS_SERVICE_URL}/transactions/{wallet_id}")
    return response.json()
