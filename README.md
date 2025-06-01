# 🚗 API Alarma Rastreadora

API REST desarrollada con FastAPI para el sistema de alarma y rastreo de vehículos con Arduino ESP32 + SIM800L + GPS.

## 📋 Características

- ✅ **Autenticación JWT** para usuarios
- ✅ **Gestión de dispositivos** vinculados a usuarios
- ✅ **Registro de ubicaciones GPS** desde Arduino
- ✅ **Sistema de alertas** en tiempo real
- ✅ **Modo seguridad** activable/desactivable
- ✅ **Base de datos MySQL** para persistencia
- ✅ **API RESTful** compatible con Flutter

## 🛠️ Instalación

### Prerrequisitos

- Python 3.8+
- MySQL Server
- Git

### 1. Clonar el proyecto

```bash
cd "c:\Users\User\Desktop\Alarma project"
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos

1. Ejecutar MySQL y crear la base de datos:

```sql
mysql -u root -p
```

```sql
CREATE DATABASE alarma_rastreadora;
```

2. Configurar variables de entorno en `.env`:

```env
MYSQL_USER=root
MYSQL_PASSWORD=tu_password_mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=alarma_rastreadora
SECRET_KEY=tu-clave-secreta-super-segura
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

La API estará disponible en: `http://localhost:8000`

## 📖 Documentación de la API

### Swagger UI
- **URL**: `http://localhost:8000/docs`
- **Descripción**: Interfaz interactiva para probar todos los endpoints

### ReDoc
- **URL**: `http://localhost:8000/redoc`
- **Descripción**: Documentación alternativa más detallada

## 🔐 Endpoints Principales

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Dispositivos
- `POST /api/dispositivos/` - Crear dispositivo
- `GET /api/dispositivos/` - Listar dispositivos del usuario
- `GET /api/dispositivos/{device_id}` - Obtener dispositivo específico
- `PUT /api/dispositivos/{device_id}` - Actualizar dispositivo
- `GET /api/dispositivos/{device_id}/modo` - **Endpoint para Arduino** - Consultar modo seguridad
- `PUT /api/dispositivos/{device_id}/modo` - Activar/desactivar modo seguridad

### Ubicaciones
- `POST /api/ubicaciones/` - **Endpoint para Arduino** - Enviar ubicación
- `GET /api/ubicaciones/device/{device_id}` - Obtener ubicaciones de dispositivo
- `GET /api/ubicaciones/device/{device_id}/latest` - Última ubicación conocida

### Alertas
- `POST /api/alertas/` - **Endpoint para Arduino** - Enviar alerta
- `GET /api/alertas/device/{device_id}` - Obtener alertas de dispositivo
- `GET /api/alertas/user` - Obtener todas las alertas del usuario
- `PUT /api/alertas/{alert_id}` - Marcar alerta como leída

## 🤖 Configuración del Arduino

### Endpoints que debe usar el Arduino:

1. **Consultar modo seguridad**: 
   ```
   GET http://tu-servidor.com/api/dispositivos/{device_id}/modo
   ```

2. **Enviar ubicación**:
   ```
   POST http://tu-servidor.com/api/ubicaciones/
   Payload: {"id": "ESP32SIM800001", "lat": -25.2637, "lng": -57.5759}
   ```

3. **Enviar alerta**:
   ```
   POST http://tu-servidor.com/api/alertas/
   Payload: {"id": "ESP32SIM800001", "evento": "movimiento", "lat": -25.2637, "lng": -57.5759}
   ```

### Actualización necesaria en el script Arduino:

Cambiar estas líneas en el código de Arduino:

```cpp
// Cambiar estas URLs por tu servidor real
String url_ubicaciones = "http://tu-servidor.com/api/ubicaciones";
String url_modo = "http://tu-servidor.com/api/dispositivos/" + deviceID + "/modo";
String url_alertas = "http://tu-servidor.com/api/alertas";
```

## 🧪 Pruebas

### Ejecutar script de prueba:

```bash
python test_api.py
```

Este script probará todos los endpoints principales y verificará que la comunicación funcione correctamente.

### Prueba manual con curl:

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'

# Iniciar sesión
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

## 📱 Integración con Flutter

### Ejemplo de configuración en Flutter:

```dart
class ApiService {
  static const String baseUrl = 'http://tu-servidor.com/api';
  
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    return jsonDecode(response.body);
  }
  
  static Future<List<dynamic>> getDevices(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/dispositivos/'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return jsonDecode(response.body);
  }
  
  static Future<void> toggleSecurityMode(String deviceId, bool enabled, String token) async {
    await http.put(
      Uri.parse('$baseUrl/dispositivos/$deviceId/modo?security_mode=$enabled'),
      headers: {'Authorization': 'Bearer $token'},
    );
  }
}
```

## 🗄️ Estructura de Base de Datos

### Tablas principales:

- **users**: Usuarios del sistema
- **devices**: Dispositivos Arduino registrados
- **locations**: Ubicaciones GPS enviadas por los dispositivos
- **alerts**: Alertas de seguridad generadas

## 🚀 Despliegue en Producción

### Variables de entorno para producción:

```env
DEBUG=False
SECRET_KEY=clave-super-secura-para-produccion
MYSQL_HOST=tu-servidor-mysql
MYSQL_USER=usuario-produccion
MYSQL_PASSWORD=password-seguro
```

### Comandos para despliegue:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar con Gunicorn
pip install gunicorn
gunicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 Desarrollo

### Estructura del proyecto:

```
alarma-rastreadora/
├── main.py              # Aplicación principal
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
├── auth_utils.py        # Utilidades de autenticación
├── routers/             # Endpoints organizados por módulo
│   ├── auth.py          # Autenticación
│   ├── users.py         # Usuarios
│   ├── devices.py       # Dispositivos
│   ├── locations.py     # Ubicaciones
│   └── alerts.py        # Alertas
├── requirements.txt     # Dependencias Python
├── .env                 # Variables de entorno
└── test_api.py         # Script de pruebas
```

## 📞 Soporte

Para preguntas o problemas, puedes:

1. Revisar la documentación en `/docs`
2. Ejecutar el script de pruebas `test_api.py`
3. Verificar los logs del servidor

## 🔄 Próximas funcionalidades

- [ ] Notificaciones push
- [ ] Dashboard web administrativo
- [ ] Geofencing (zonas de seguridad)
- [ ] Historial de rutas
- [ ] Múltiples tipos de sensores
- [ ] Integración con servicios de mapas
