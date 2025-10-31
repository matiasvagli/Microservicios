

from fastapi import FastAPI
from core.middleware import JWTMiddleware
from proxies.auth_proxy import router as auth_router
from proxies.wallet_proxy import router as wallet_router
from proxies.transactions_proxy import router as transactions_router

app = FastAPI(title="API Gateway")

# 👇 Agregamos el middleware JWT
app.add_middleware(JWTMiddleware)

# Routers
app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transactions_router)

@app.get("/")
def root():
    return {"message": "API Gateway OK"}







