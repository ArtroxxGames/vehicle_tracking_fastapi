from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from database import get_db, engine
from models import Base
from routers import auth, users, devices, locations, alerts
from auth_utils import verify_token

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Alarma Rastreadora",
    description="API para sistema de alarma y rastreo de vehículos con Arduino",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(devices.router, prefix="/api/dispositivos", tags=["Dispositivos"])
app.include_router(locations.router, prefix="/api/ubicaciones", tags=["Ubicaciones"])
app.include_router(alerts.router, prefix="/api/alertas", tags=["Alertas"])

@app.get("/")
async def root():
    return {"message": "API Alarma Rastreadora v1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
