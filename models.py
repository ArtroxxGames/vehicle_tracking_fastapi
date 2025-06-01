from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con dispositivos
    devices = relationship("Device", back_populates="owner")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)  # ID del Arduino
    name = Column(String(100), nullable=False)  # Nombre descriptivo del dispositivo
    description = Column(Text, nullable=True)
    vehicle_type = Column(String(50), nullable=True)  # carro, moto, bicicleta
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    security_mode = Column(Boolean, default=False)  # Modo seguridad activado/desactivado
    is_active = Column(Boolean, default=True)
    last_ping = Column(DateTime, nullable=True)  # Última vez que el dispositivo se comunicó
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner = relationship("User", back_populates="devices")
    locations = relationship("Location", back_populates="device")
    alerts = relationship("Alert", back_populates="device")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # Precisión del GPS
    speed = Column(Float, nullable=True)  # Velocidad si está disponible
    altitude = Column(Float, nullable=True)  # Altitud si está disponible
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    device = relationship("Device", back_populates="locations")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # movimiento, bateria_baja, etc.
    message = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_read = Column(Boolean, default=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    device = relationship("Device", back_populates="alerts")
