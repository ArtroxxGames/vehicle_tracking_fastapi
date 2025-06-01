from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Device, User
from schemas import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceModeResponse
from auth_utils import verify_token, get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=DeviceResponse)
async def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Crear nuevo dispositivo"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Verificar si el device_id ya existe
    existing_device = db.query(Device).filter(Device.device_id == device.device_id).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID del dispositivo ya existe"
        )
    
    db_device = Device(
        device_id=device.device_id,
        name=device.name,
        description=device.description,
        vehicle_type=device.vehicle_type,
        owner_id=current_user.id
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device

@router.get("/", response_model=List[DeviceResponse])
async def get_user_devices(
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener todos los dispositivos del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    devices = db.query(Device).filter(
        Device.owner_id == current_user.id,
        Device.is_active == True
    ).all()
    
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener un dispositivo específico"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Actualizar dispositivo"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Actualizar campos si se proporcionan
    if device_update.name is not None:
        device.name = device_update.name
    if device_update.description is not None:
        device.description = device_update.description
    if device_update.vehicle_type is not None:
        device.vehicle_type = device_update.vehicle_type
    if device_update.security_mode is not None:
        device.security_mode = device_update.security_mode
    if device_update.is_active is not None:
        device.is_active = device_update.is_active
    
    device.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(device)
    
    return device

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Eliminar dispositivo"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Marcar como inactivo en lugar de eliminar
    device.is_active = False
    device.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Dispositivo eliminado exitosamente"}

# Endpoint especial para el Arduino - consultar modo seguridad
@router.get("/{device_id}/modo", response_model=DeviceModeResponse)
async def get_security_mode(device_id: str, db: Session = Depends(get_db)):
    """Endpoint para que el Arduino consulte el modo de seguridad"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.is_active == True
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Actualizar last_ping
    device.last_ping = datetime.utcnow()
    db.commit()
    
    return DeviceModeResponse(
        device_id=device.device_id,
        modo_seguridad=device.security_mode
    )

# Endpoint para activar/desactivar modo seguridad desde la app
@router.put("/{device_id}/modo")
async def toggle_security_mode(
    device_id: str,
    security_mode: bool,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Activar/desactivar modo de seguridad"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    device.security_mode = security_mode
    device.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": f"Modo de seguridad {'activado' if security_mode else 'desactivado'}",
        "device_id": device.device_id,
        "security_mode": security_mode
    }
