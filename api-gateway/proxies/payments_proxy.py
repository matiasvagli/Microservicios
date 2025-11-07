from fastapi import APIRouter, Request, Response
import httpx
import os

router = APIRouter(prefix="/payments", tags=["Payments"])

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:8004")

@router.post("/deposit")
async def proxy_deposit(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{PAYMENT_SERVICE_URL}/payments/deposit", content=body, headers=headers)
    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
