from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Location, Device
from schemas import LocationCreate, LocationResponse
from auth_utils import verify_token, get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Endpoint para que el Arduino envíe ubicaciones"""
    # Buscar el dispositivo por device_id
    device = db.query(Device).filter(
        Device.device_id == location.id,
        Device.is_active == True
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Crear nueva ubicación
    db_location = Location(
        device_id=device.id,
        latitude=location.lat,
        longitude=location.lng,
        timestamp=datetime.utcnow()
    )
    
    # Actualizar last_ping del dispositivo
    device.last_ping = datetime.utcnow()
    
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    return {"message": "Ubicación registrada exitosamente", "id": db_location.id}

@router.get("/device/{device_id}", response_model=List[LocationResponse])
async def get_device_locations(
    device_id: str,
    limit: Optional[int] = 50,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener ubicaciones de un dispositivo específico"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Verificar que el dispositivo pertenece al usuario
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Obtener ubicaciones ordenadas por fecha (más recientes primero)
    locations = db.query(Location).filter(
        Location.device_id == device.id
    ).order_by(desc(Location.timestamp)).limit(limit).all()
    
    return locations

@router.get("/device/{device_id}/latest", response_model=LocationResponse)
async def get_latest_location(
    device_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener la última ubicación conocida de un dispositivo"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Verificar que el dispositivo pertenece al usuario
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Obtener la última ubicación
    latest_location = db.query(Location).filter(
        Location.device_id == device.id
    ).order_by(desc(Location.timestamp)).first()
    
    if not latest_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ubicaciones registradas para este dispositivo"
        )
    
    return latest_location

@router.get("/user", response_model=List[LocationResponse])
async def get_user_locations(
    limit: Optional[int] = 100,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener todas las ubicaciones de los dispositivos del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Obtener todos los dispositivos del usuario
    user_devices = db.query(Device).filter(
        Device.owner_id == current_user.id,
        Device.is_active == True
    ).all()
    
    device_ids = [device.id for device in user_devices]
    
    # Obtener ubicaciones de todos sus dispositivos
    locations = db.query(Location).filter(
        Location.device_id.in_(device_ids)
    ).order_by(desc(Location.timestamp)).limit(limit).all()
    
    return locations

@router.delete("/device/{device_id}")
async def delete_device_locations(
    device_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Eliminar todas las ubicaciones de un dispositivo"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Verificar que el dispositivo pertenece al usuario
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Eliminar todas las ubicaciones del dispositivo
    deleted_count = db.query(Location).filter(
        Location.device_id == device.id
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Se eliminaron {deleted_count} ubicaciones del dispositivo {device_id}"
    }
