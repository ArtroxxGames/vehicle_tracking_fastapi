import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_backend():
    # 1. Test health
    print("🏥 Probando health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health: {response.json()}")
    except Exception as e:
        print(f"❌ Health error: {e}")
    
    # 2. Test login
    print("\n🔐 Probando login...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print(f"✅ Login exitoso! Token: {token[:30]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. Test devices
            print("\n📱 Probando dispositivos...")
            devices_response = requests.get(f"{BASE_URL}/dispositivos/", headers=headers)
            if devices_response.status_code == 200:
                devices = devices_response.json()
                print(f"✅ Dispositivos: {len(devices)} encontrados")
                print(f"   Tipo de respuesta: {type(devices)}")
                if devices:
                    print(f"   Primer dispositivo: {devices[0].get('name', 'N/A')}")
            else:
                print(f"❌ Dispositivos error: {devices_response.status_code} - {devices_response.text}")
            
            # 4. Test alerts
            print("\n🚨 Probando alertas...")
            alerts_response = requests.get(f"{BASE_URL}/alertas/user", headers=headers)
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                print(f"✅ Alertas: {len(alerts)} encontradas")
                print(f"   Tipo de respuesta: {type(alerts)}")
                if alerts:
                    print(f"   Primera alerta: {alerts[0].get('message', 'N/A')}")
            else:
                print(f"❌ Alertas error: {alerts_response.status_code} - {alerts_response.text}")
                
        else:
            print(f"❌ Login error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_backend()
