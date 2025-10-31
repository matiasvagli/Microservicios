from fastapi import FastAPI
from app.routes.auth_routes import router as auth_router
from app.db.connection import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Auth Service", description="Servicio de autenticación de usuarios")

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "Auth Service OK"}
