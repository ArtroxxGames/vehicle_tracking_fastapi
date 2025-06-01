from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Alert, Device
from schemas import AlertCreate, AlertUpdate, AlertResponse
from auth_utils import verify_token, get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Endpoint para que el Arduino envíe alertas"""
    # Buscar el dispositivo por device_id
    device = db.query(Device).filter(
        Device.device_id == alert.id,
        Device.is_active == True
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    # Mapear tipos de eventos
    event_messages = {
        "movimiento": "Movimiento detectado mientras el modo seguridad estaba activado",
        "bateria_baja": "Batería del dispositivo está baja",
        "gps_perdido": "Señal GPS perdida",
        "tamper": "Intento de manipulación del dispositivo detectado"
    }
    
    # Determinar severidad según el tipo de evento
    severity_map = {
        "movimiento": "high",
        "bateria_baja": "medium",
        "gps_perdido": "medium",
        "tamper": "critical"
    }
    
    # Crear nueva alerta
    db_alert = Alert(
        device_id=device.id,
        alert_type=alert.evento,
        message=event_messages.get(alert.evento, f"Evento: {alert.evento}"),
        latitude=alert.lat,
        longitude=alert.lng,
        severity=severity_map.get(alert.evento, "medium"),
        timestamp=datetime.utcnow()
    )
    
    # Actualizar last_ping del dispositivo
    device.last_ping = datetime.utcnow()
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return {"message": "Alerta registrada exitosamente", "id": db_alert.id}

@router.get("/device/{device_id}", response_model=List[AlertResponse])
async def get_device_alerts(
    device_id: str,
    limit: Optional[int] = 50,
    unread_only: Optional[bool] = False,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener alertas de un dispositivo específico"""
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
    
    # Construir query
    query = db.query(Alert).filter(Alert.device_id == device.id)
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    # Obtener alertas ordenadas por fecha (más recientes primero)
    alerts = query.order_by(desc(Alert.timestamp)).limit(limit).all()
    
    return alerts

@router.get("/user", response_model=List[AlertResponse])
async def get_user_alerts(
    limit: Optional[int] = 100,
    unread_only: Optional[bool] = False,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener todas las alertas de los dispositivos del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Obtener todos los dispositivos del usuario
    user_devices = db.query(Device).filter(
        Device.owner_id == current_user.id,
        Device.is_active == True
    ).all()
    
    device_ids = [device.id for device in user_devices]
    
    # Construir query
    query = db.query(Alert).filter(Alert.device_id.in_(device_ids))
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    
    # Obtener alertas ordenadas por fecha (más recientes primero)
    alerts = query.order_by(desc(Alert.timestamp)).limit(limit).all()
    
    return alerts

@router.get("/user/unread/count")
async def get_unread_alerts_count(
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Obtener el número de alertas no leídas del usuario"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Obtener todos los dispositivos del usuario
    user_devices = db.query(Device).filter(
        Device.owner_id == current_user.id,
        Device.is_active == True
    ).all()
    
    device_ids = [device.id for device in user_devices]
    
    # Contar alertas no leídas
    unread_count = db.query(Alert).filter(
        Alert.device_id.in_(device_ids),
        Alert.is_read == False
    ).count()
    
    return {"unread_count": unread_count}

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Actualizar una alerta (marcar como leída, cambiar severidad, etc.)"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Verificar que la alerta pertenece a un dispositivo del usuario
    alert = db.query(Alert).join(Device).filter(
        Alert.id == alert_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    # Actualizar campos si se proporcionan
    if alert_update.is_read is not None:
        alert.is_read = alert_update.is_read
    if alert_update.severity is not None:
        alert.severity = alert_update.severity
    
    db.commit()
    db.refresh(alert)
    
    return alert

@router.put("/mark-all-read")
async def mark_all_alerts_read(
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Marcar todas las alertas como leídas"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Obtener dispositivos del usuario
    user_devices_query = db.query(Device).filter(
        Device.owner_id == current_user.id,
        Device.is_active == True
    )
    
    if device_id:
        user_devices_query = user_devices_query.filter(Device.device_id == device_id)
    
    user_devices = user_devices_query.all()
    device_ids = [device.id for device in user_devices]
    
    if not device_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron dispositivos"
        )
    
    # Actualizar todas las alertas no leídas
    updated_count = db.query(Alert).filter(
        Alert.device_id.in_(device_ids),
        Alert.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": f"Se marcaron {updated_count} alertas como leídas"}

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    """Eliminar una alerta específica"""
    email = verify_token(token)
    current_user = get_current_user(db, email)
    
    # Verificar que la alerta pertenece a un dispositivo del usuario
    alert = db.query(Alert).join(Device).filter(
        Alert.id == alert_id,
        Device.owner_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alerta eliminada exitosamente"}
