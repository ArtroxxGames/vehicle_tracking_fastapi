"""
Script de ejemplo para probar los endpoints de la API
Requiere requests: pip install requests
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000/api"

def test_api():
    print("🚀 Probando API de Alarma Rastreadora")
    
    # 1. Registrar usuario
    print("\n1. Registrando usuario...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Usuario de Prueba",
        "phone": "+595981234567"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Usuario registrado exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 2. Iniciar sesión
    print("\n2. Iniciando sesión...")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Sesión iniciada exitosamente")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # 3. Crear dispositivo
    print("\n3. Creando dispositivo...")
    device_data = {
        "device_id": "ESP32SIM800001",
        "name": "Mi Motocicleta",
        "description": "Honda CB650R 2023",
        "vehicle_type": "motocicleta"
    }
    
    response = requests.post(f"{BASE_URL}/dispositivos/", json=device_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Dispositivo creado exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 4. Activar modo seguridad
    print("\n4. Activando modo seguridad...")
    response = requests.put(f"{BASE_URL}/dispositivos/ESP32SIM800001/modo?security_mode=true", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Modo seguridad activado")
    else:
        print(f"❌ Error: {response.text}")
    
    # 5. Simular envío de ubicación desde Arduino
    print("\n5. Simulando envío de ubicación desde Arduino...")
    location_data = {
        "id": "ESP32SIM800001",
        "lat": -25.2637,
        "lng": -57.5759
    }
    
    response = requests.post(f"{BASE_URL}/ubicaciones/", json=location_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Ubicación enviada exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 6. Simular envío de alerta desde Arduino
    print("\n6. Simulando envío de alerta desde Arduino...")
    alert_data = {
        "id": "ESP32SIM800001",
        "evento": "movimiento",
        "lat": -25.2637,
        "lng": -57.5759
    }
    
    response = requests.post(f"{BASE_URL}/alertas/", json=alert_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Alerta enviada exitosamente")
    else:
        print(f"❌ Error: {response.text}")
    
    # 7. Obtener alertas del usuario
    print("\n7. Obteniendo alertas del usuario...")
    response = requests.get(f"{BASE_URL}/alertas/user", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"✅ Se encontraron {len(alerts)} alertas")
        for alert in alerts:
            print(f"   - {alert['alert_type']}: {alert['message']}")
    else:
        print(f"❌ Error: {response.text}")
    
    # 8. Verificar modo seguridad desde Arduino
    print("\n8. Verificando modo seguridad desde Arduino...")
    response = requests.get(f"{BASE_URL}/dispositivos/ESP32SIM800001/modo")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        mode_data = response.json()
        print(f"✅ Modo seguridad: {'ACTIVADO' if mode_data['modo_seguridad'] else 'DESACTIVADO'}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que la API esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
