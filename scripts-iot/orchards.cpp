#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ----------------------------
// CONFIGURACIÓN DE HARDWARE (Ajustada para ESP32-S3)
// ----------------------------
#define DHTPIN 4
#define DHTTYPE DHT11
#define SOIL_MOISTURE_PIN 15
#define WATER_SENSOR_PIN 5
#define PUMP_PIN 6
#define BOMBA_STATE_PIN 19

const int dryValue = 4095;  // Valor para suelo seco
const int wetValue = 2000;  // Valor para suelo húmedo

// ----------------------------
// CONFIGURACIÓN DE RED (Modifica con tus credenciales)
// ----------------------------
const char* ssid = "Sala de Juntas";
const char* password = "";

// ----------------------------
// CONFIGURACIÓN MQTT (Considera usar variables más seguras)
// ----------------------------
const char* mqtt_server = "jaragua-01.lmq.cloudamqp.com";
const int mqtt_port = 1883;
const char* mqtt_user = "kufvoati";
const char* mqtt_password = "U80l2J0lRbj84BceoCF0lYVRdPe_a9rD";
const char* huerta_id = "huerta_01";
const char* mqtt_topic = "huerta";  // Cambiado a const char* para evitar objetos String

// ----------------------------
// OBJETOS GLOBALES
// ----------------------------
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 10000;

// ----------------------------
// PROTOTIPOS DE FUNCIÓN
// ----------------------------
void setup_wifi();
void reconnect_mqtt();
void readAndSendData();
void checkHardware();

// ----------------------------
// FUNCIONES
// ----------------------------
void setup_wifi() {
  Serial.println();
  Serial.print("🔌 Conectando a ");
  Serial.println(ssid);

  WiFi.disconnect(true);  // Asegura que no hay conexiones previas
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  unsigned long startAttempt = millis();
  
  while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 15000) {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi conectado");
    Serial.print("📶 Dirección IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Fallo al conectar WiFi. Modo offline activado.");
  }
}

void reconnect_mqtt() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  if (!client.connected()) {
    Serial.print("🔄 Intentando conexión MQTT...");
    
    // Crear un ID de cliente único agregando los últimos bytes de la MAC
    String clientId = "ESP32Client-";
    uint8_t mac[6];
    WiFi.macAddress(mac);
    clientId += String(mac[3], HEX);
    clientId += String(mac[4], HEX);
    clientId += String(mac[5], HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("✅ Conectado a MQTT");
    } else {
      Serial.print("❌ falló, rc=");
      Serial.print(client.state());
      Serial.println(" intentando de nuevo en 5 segundos");
      delay(5000);  // Espera antes de reintentar
    }
  }
}

void readAndSendData() {
  // Verificar hardware primero
  checkHardware();

  // Leer sensores
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  if (isnan(humidity)) {
    Serial.println("⚠️ Error al leer humedad del DHT11");
    humidity = -1.0;  // Valor de error
  }
  
  if (isnan(temperature)) {
    Serial.println("⚠️ Error al leer temperatura del DHT11");
    temperature = -1.0;  // Valor de error
  }

  int rawMoisture = analogRead(SOIL_MOISTURE_PIN);
  float moisturePercentage = constrain(map(rawMoisture, dryValue, wetValue, 0, 100), 0, 100);
  bool waterDetected = !digitalRead(WATER_SENSOR_PIN);  // Invertido si es sensor de nivel de agua
  bool bombaState = digitalRead(BOMBA_STATE_PIN);

  // Crear JSON
  DynamicJsonDocument doc(256);
  doc["id"] = huerta_id;
  doc["temperature"] = temperature;
  doc["air_humidity"] = humidity;
  doc["soil_moisture"] = moisturePercentage;
  doc["water_detected"] = waterDetected;
  doc["pump_state"] = bombaState;

  char payload[256];
  size_t n = serializeJson(doc, payload);

  // Enviar si hay conexión
  if (client.connected()) {
    if (client.publish(mqtt_topic, payload, n)) {
      Serial.println("📤 Datos enviados:");
      Serial.println(payload);
    } else {
      Serial.println("❌ Error al enviar mensaje MQTT");
    }
  } else {
    Serial.println("⚠️ MQTT no conectado. Mensaje no enviado.");
    Serial.println(payload);  // Mostrar datos igualmente
  }
}

void checkHardware() {
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck < 5000) return;  // Verificar cada 5 segundos
  
  lastCheck = millis();
  
  Serial.println("🛠️ Verificación de hardware:");
  Serial.print("  - DHT11: ");
  Serial.println(dht.readHumidity() != NAN ? "OK" : "ERROR");
  Serial.print("  - Humedad suelo: ");
  Serial.println(analogRead(SOIL_MOISTURE_PIN));
  Serial.print("  - Sensor agua: ");
  Serial.println(digitalRead(WATER_SENSOR_PIN) ? "SECO" : "AGUA DETECTADA");
  Serial.print("  - Estado bomba: ");
  Serial.println(digitalRead(BOMBA_STATE_PIN) ? "ENCENDIDA" : "APAGADA");
}

// ----------------------------
// SETUP
// ----------------------------
void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 5000);  // Esperar hasta 5 segundos por el monitor serial

  Serial.println("\n🌱 Iniciando sistema de monitoreo de huerta 🌱");
  
  // Inicializar hardware
  dht.begin();
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(WATER_SENSOR_PIN, INPUT_PULLUP);  // Usar resistencia pull-up interna
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(BOMBA_STATE_PIN, INPUT);
  digitalWrite(PUMP_PIN, LOW);

  // Iniciar WiFi y MQTT
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setBufferSize(512);  // Aumentar buffer para mensajes MQTT
  client.setSocketTimeout(5); // Tiempo de espera más corto
}

// ----------------------------
// LOOP PRINCIPAL
// ----------------------------
void loop() {
  // Manejo de conexiones
  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long lastReconnectAttempt = 0;
    if (millis() - lastReconnectAttempt > 15000) {  // Reintentar cada 15 segundos
      lastReconnectAttempt = millis();
      setup_wifi();
    }
  } else {
    if (!client.connected()) {
      reconnect_mqtt();
    }
    client.loop();
  }

  // Envío periódico de datos
  static unsigned long lastDataSend = 0;
  if (millis() - lastDataSend >= sendInterval) {
    lastDataSend = millis();
    readAndSendData();
  }

  // Pequeña pausa para evitar sobrecarga
  delay(10);
}