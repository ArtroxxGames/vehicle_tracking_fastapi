import sys
import os
import sys
from datetime import datetime, timedelta
import random

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import User, Device, Location, Alert
from auth_utils import get_password_hash

def create_test_data():
    """Crear datos de prueba para la aplicación."""
    db = next(get_db())
    
    try:
        # Crear usuario de prueba
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Usuario de Prueba"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Usuario creado: {test_user.email}")
        else:
            print(f"Usuario existente: {test_user.email}")        # Crear dispositivo de prueba
        test_device = db.query(Device).filter(Device.device_id == "ESP32_001").first()
        if not test_device:
            test_device = Device(
                name="Vehículo de Prueba",
                device_id="ESP32_001",
                description="Dispositivo para pruebas de la aplicación",
                vehicle_type="auto",
                owner_id=test_user.id,
                is_active=True,
                security_mode=True
            )
            db.add(test_device)
            db.commit()
            db.refresh(test_device)
            print(f"Dispositivo creado: {test_device.name}")
        else:
            print(f"Dispositivo existente: {test_device.name}")

        # Crear ubicaciones de prueba (simulando un recorrido por una ciudad)
        locations_data = [
            {"lat": 4.7110, "lng": -74.0721, "hours_ago": 0},      # Bogotá Centro
            {"lat": 4.7100, "lng": -74.0725, "hours_ago": 0.5},   # Moviéndose
            {"lat": 4.7090, "lng": -74.0730, "hours_ago": 1},     # 
            {"lat": 4.7080, "lng": -74.0735, "hours_ago": 1.5},   #
            {"lat": 4.7070, "lng": -74.0740, "hours_ago": 2},     #
            {"lat": 4.7060, "lng": -74.0745, "hours_ago": 2.5},   #
            {"lat": 4.7050, "lng": -74.0750, "hours_ago": 3},     # Recorrido
            {"lat": 4.7040, "lng": -74.0755, "hours_ago": 3.5},   #
            {"lat": 4.7030, "lng": -74.0760, "hours_ago": 4},     #
            {"lat": 4.7020, "lng": -74.0765, "hours_ago": 4.5},   #
        ]

        # Eliminar ubicaciones existentes del dispositivo
        db.query(Location).filter(Location.device_id == test_device.id).delete()
        
        for i, loc_data in enumerate(locations_data):
            timestamp = datetime.now() - timedelta(hours=loc_data["hours_ago"])
            speed = random.uniform(0, 60) if i > 0 else 0  # Velocidad aleatoria
            
            location = Location(
                device_id=test_device.id,
                latitude=loc_data["lat"],
                longitude=loc_data["lng"],
                timestamp=timestamp,
                speed=speed
            )
            db.add(location)
        
        # Crear algunas alertas de prueba
        alert_types = ["motion_detected", "low_battery", "gps_lost"]
        for i in range(3):
            alert = Alert(
                device_id=test_device.id,
                alert_type=alert_types[i],
                message=f"Alerta de prueba {i+1}: {alert_types[i].replace('_', ' ').title()}",
                timestamp=datetime.now() - timedelta(hours=i),
                is_read=i > 0  # Primera alerta sin leer
            )
            db.add(alert)

        db.commit()
        print(f"Se crearon {len(locations_data)} ubicaciones de prueba")
        print("Se crearon 3 alertas de prueba")
        print("\n✅ Datos de prueba creados exitosamente!")
        print("\nCredenciales de acceso:")
        print("Email: test@example.com")
        print("Password: password123")
        
    except Exception as e:
        db.rollback()
        print(f"Error al crear datos de prueba: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
