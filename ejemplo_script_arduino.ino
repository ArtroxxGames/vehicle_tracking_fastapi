#include <HardwareSerial.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

// Pines
#define SENSOR_MOVIMIENTO 27
#define PIN_RX_SIM800 16
#define PIN_TX_SIM800 17
#define PIN_RX_GPS 4
#define PIN_TX_GPS 2

// Configuración de los módulos
TinyGPSPlus gps;
HardwareSerial sim800(1);
SoftwareSerial gpsSerial(PIN_RX_GPS, PIN_TX_GPS); // RX, TX

// Estado
bool modoSeguridad = false; // Se actualiza desde el servidor
String deviceID = "ESP32SIM800001"; // ID único del dispositivo

// Coordenadas actuales
struct Ubicacion {
  double lat;
  double lng;
  bool valida;
} ubicacionActual;

// ---------------------------- SETUP ----------------------------

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600);
  sim800.begin(9600, SERIAL_8N1, PIN_RX_SIM800, PIN_TX_SIM800);
  pinMode(SENSOR_MOVIMIENTO, INPUT);

  delay(3000);
  Serial.println("Iniciando ESP32 con SIM800L + GPS...");

  configurarGPRS();
}

// ---------------------------- LOOP PRINCIPAL ----------------------------

void loop() {
  leerGPS();

  // Consultar al servidor si está activado el modo de seguridad
  actualizarModoSeguridad();

  // Enviar la ubicación al servidor si es válida
  if (ubicacionActual.valida) {
    enviarDatosGPS();
  }

  // Si se detecta movimiento y el modo está activado, enviar alerta
  if (digitalRead(SENSOR_MOVIMIENTO) == HIGH && modoSeguridad) {
    enviarAlertaMovimiento();
  }

  delay(10000); // Esperar 10 segundos antes del próximo ciclo
}

// ---------------------------- FUNCIONES ----------------------------

// Configurar conexión GPRS para datos móviles
void configurarGPRS() {
  sim800.println("AT");
  delay(1000);
  sim800.println("AT+SAPBR=3,1,\"Contype\",\"GPRS\"");
  delay(1000);
  sim800.println("AT+SAPBR=3,1,\"APN\",\"internet.tigo.py\""); // Cambia según tu operadora
  delay(1000);
  sim800.println("AT+SAPBR=1,1"); // Activar portador GPRS
  delay(3000);
}

// Leer datos GPS desde el módulo y guardar posición
void leerGPS() {
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  if (gps.location.isValid()) {
    ubicacionActual.lat = gps.location.lat();
    ubicacionActual.lng = gps.location.lng();
    ubicacionActual.valida = true;
    Serial.println("Ubicación válida: Lat=" + String(ubicacionActual.lat) + " Lng=" + String(ubicacionActual.lng));
  } else {
    ubicacionActual.valida = false;
    Serial.println("Ubicación inválida");
  }
}

// Enviar datos de ubicación al servidor por POST
void enviarDatosGPS() {
  String url = "https://tuservidor.com/api/ubicaciones"; // CAMBIA esto a tu endpoint real

  // Construir JSON manual
  String postData = "{\"id\":\"" + deviceID + "\",\"lat\":" + String(ubicacionActual.lat, 6) +
                    ",\"lng\":" + String(ubicacionActual.lng, 6) + "}";

  sim800.println("AT+HTTPTERM");
  delay(500);
  sim800.println("AT+HTTPINIT");
  delay(500);
  sim800.println("AT+HTTPPARA=\"CID\",1");
  delay(500);
  sim800.println("AT+HTTPPARA=\"URL\",\"" + url + "\"");
  delay(500);
  sim800.println("AT+HTTPPARA=\"CONTENT\",\"application/json\"");
  delay(500);

  // Especificar el cuerpo del POST
  sim800.println("AT+HTTPDATA=" + String(postData.length()) + ",10000");
  delay(1000);
  sim800.print(postData);
  delay(1000);

  sim800.println("AT+HTTPACTION=1"); // 1 = POST
  delay(6000);

  Serial.println("Datos GPS enviados al servidor.");
  sim800.println("AT+HTTPTERM");
}

// Consultar al servidor el estado del modo de seguridad (GET)
void actualizarModoSeguridad() {
  String url = "https://tuservidor.com/api/dispositivos/" + deviceID + "/modo"; // CAMBIA esto

  sim800.println("AT+HTTPTERM");
  delay(500);
  sim800.println("AT+HTTPINIT");
  delay(500);
  sim800.println("AT+HTTPPARA=\"CID\",1");
  delay(500);
  sim800.println("AT+HTTPPARA=\"URL\",\"" + url + "\"");
  delay(1000);
  sim800.println("AT+HTTPACTION=0"); // 0 = GET
  delay(6000);

  sim800.println("AT+HTTPREAD");
  delay(1000);

  String respuesta = "";
  while (sim800.available()) {
    char c = sim800.read();
    respuesta += c;
  }

  sim800.println("AT+HTTPTERM");

  // Parsear respuesta manualmente
  if (respuesta.indexOf("\"modo_seguridad\":true") != -1) {
    modoSeguridad = true;
  } else if (respuesta.indexOf("\"modo_seguridad\":false") != -1) {
    modoSeguridad = false;
  }

  Serial.println("Modo Seguridad actualizado: " + String(modoSeguridad ? "ACTIVADO" : "DESACTIVADO"));
}

// Enviar alerta de movimiento al servidor
void enviarAlertaMovimiento() {
  String url = "https://tuservidor.com/api/alertas"; // CAMBIA esto

  String postData = "{\"id\":\"" + deviceID + "\",\"evento\":\"movimiento\",\"lat\":" + 
                    String(ubicacionActual.lat, 6) + ",\"lng\":" + String(ubicacionActual.lng, 6) + "}";

  sim800.println("AT+HTTPTERM");
  delay(500);
  sim800.println("AT+HTTPINIT");
  delay(500);
  sim800.println("AT+HTTPPARA=\"CID\",1");
  delay(500);
  sim800.println("AT+HTTPPARA=\"URL\",\"" + url + "\"");
  delay(500);
  sim800.println("AT+HTTPPARA=\"CONTENT\",\"application/json\"");
  delay(500);
  sim800.println("AT+HTTPDATA=" + String(postData.length()) + ",10000");
  delay(1000);
  sim800.print(postData);
  delay(1000);

  sim800.println("AT+HTTPACTION=1");
  delay(6000);

  Serial.println("¡Alerta de movimiento enviada!");
  sim800.println("AT+HTTPTERM");
}