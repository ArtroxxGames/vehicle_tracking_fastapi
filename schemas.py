from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Esquemas para Usuarios
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Esquemas para Dispositivos
class DeviceBase(BaseModel):
    device_id: str
    name: str
    description: Optional[str] = None
    vehicle_type: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    vehicle_type: Optional[str] = None
    security_mode: Optional[bool] = None
    is_active: Optional[bool] = None

class DeviceResponse(DeviceBase):
    id: int
    owner_id: int
    security_mode: bool
    is_active: bool
    last_ping: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DeviceModeResponse(BaseModel):
    device_id: str
    modo_seguridad: bool

# Esquemas para Ubicaciones
class LocationBase(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    altitude: Optional[float] = None

class LocationCreate(BaseModel):
    id: str  # device_id del Arduino
    lat: float
    lng: float

class LocationResponse(LocationBase):
    id: int
    device_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Esquemas para Alertas
class AlertBase(BaseModel):
    alert_type: str
    message: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    severity: Optional[str] = "medium"

class AlertCreate(BaseModel):
    id: str  # device_id del Arduino
    evento: str  # tipo de evento
    lat: Optional[float] = None
    lng: Optional[float] = None

class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    severity: Optional[str] = None

class AlertResponse(AlertBase):
    id: int
    device_id: int
    is_read: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Esquemas para respuestas con paginación
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int
