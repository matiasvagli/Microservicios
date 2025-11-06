from fastapi import FastAPI
from routers import payments

app = FastAPI(
    title="Payment Service",
    description="Simula un gateway de pagos que emite eventos hacia el Wallet Service",
    version="1.0.0"
)

# Registrar routers
app.include_router(payments.router)

@app.get("/")
def root():
    return {"message": "Payment Service running 🚀"}
