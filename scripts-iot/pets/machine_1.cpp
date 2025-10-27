#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <Preferences.h>  
Preferences prefs;

// Configuración WiFi y BLE
String wifiSSID = "";
String wifiPassword = ""; 
bool credentialsReceived = false;
bool wifiConnected = false;
unsigned long wifiConnectionStartTime = 0;
const int WIFI_TIMEOUT = 20000;
bool isSSIDReceived = false;
bool isPasswordReceived = false;

// UUIDs para BLE
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID_SSID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHARACTERISTIC_UUID_PASS "beb5483e-36e1-4688-b7f5-ea07361b26a9"

// Configuración MQTT
const char* mqtt_server = "jaragua-01.lmq.cloudamqp.com";
const int mqtt_port = 1883;
const char* mqtt_user = "kufvoati:kufvoati";
const char* mqtt_password = "U80l2J0lRbj84BceoCF0lYVRdPe_a9rD";
const char* mqtt_topic = "pets/dispense";

// Configuración del servo y botón
const int servoPin = 4;
const int feedButton = 2;
const int resetButtonPin  = 12;
bool isRotating = false;
const int rotationTime = 1050;
unsigned long rotationStartTime = 0;
Servo servo;

// Variables del botón
int lastButtonState = HIGH;
int buttonState;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

// Variables MQTT y WiFi
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMqttAttempt = 0;
const unsigned long mqttRetryInterval = 5000;

// Variables de control del servo
unsigned long lastRotationTime = 0;
int currentRotations = 0;
int targetRotations = 0;

// Declaraciones de funciones
void connectToWiFi();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void reconnectMqtt();

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        String value = pCharacteristic->getValue().c_str();
        Serial.println("Algo llegó");
        if (pCharacteristic->getUUID().toString() == CHARACTERISTIC_UUID_SSID) {
            wifiSSID = value;
            isSSIDReceived = true;
            Serial.print("SSID recibido: ");
            Serial.println(wifiSSID);
        } 
        else if (pCharacteristic->getUUID().toString() == CHARACTERISTIC_UUID_PASS) {
            wifiPassword = value;
            isPasswordReceived = true;
            Serial.print("Contraseña recibida: ");
            Serial.println(wifiPassword);
        }
        
        if (isSSIDReceived && isPasswordReceived) {
            credentialsReceived = true;
            Serial.println("\nCredenciales completas recibidas:");
            Serial.println("===============================");
            Serial.print("SSID: ");
            Serial.println(wifiSSID);
            Serial.print("Contraseña: ");
            Serial.println(wifiPassword);
            Serial.println("Intentando conectar a WiFi...");
            Serial.println("===============================\n");

            connectToWiFi();

            prefs.putString("ssid", wifiSSID);
            prefs.putString("pass", wifiPassword);
            Serial.println("Credenciales guardadas en NVS");
        }
    }
};

void connectToWiFi() {
    Serial.println("Conectando a WiFi...");
    
    WiFi.begin(wifiSSID.c_str(), wifiPassword.c_str());
    wifiConnectionStartTime = millis();
    
    while (WiFi.status() != WL_CONNECTED && 
           millis() - wifiConnectionStartTime < WIFI_TIMEOUT) {
        delay(500);
        Serial.print(".");
        yield();
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifiConnected = true;
        Serial.println("\n¡Conectado a WiFi!");
        Serial.print("Dirección IP: ");
        Serial.println(WiFi.localIP());
        
        BLEDevice::stopAdvertising();
        Serial.println("Publicidad BLE detenida");
        
        // Configura cliente MQTT pero no bloquea
        client.setServer(mqtt_server, mqtt_port);
        client.setCallback(mqttCallback);
    } else {
        Serial.println("\nError: No se pudo conectar al WiFi");
        Serial.println("Verifica las credenciales y asegúrate que la red está disponible");
        credentialsReceived = false;
    }
}

void reconnectMqtt() {
    if (!client.connected() && millis() - lastMqttAttempt > mqttRetryInterval) {
        lastMqttAttempt = millis();
        Serial.print("Intentando conectar a MQTT...");
        
        if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
            Serial.println("Conectado");
            client.subscribe(mqtt_topic);
        } else {
            Serial.print("falló, rc=");
            Serial.print(client.state());
            Serial.println(" intentando de nuevo en 5 segundos");
        }
    }
}

// ---------- MANEJO DE CREDENCIALES ----------
void eraseCredentials() {
  Serial.println("\n*** BORRANDO credenciales WiFi ***");
  prefs.clear();                      // elimina todas las claves del namespace
  prefs.end();                        // cierra antes de reiniciar (opcional)
  delay(200);                         // deja acabar el print
  ESP.restart();                      // reinicia la placa
}

void startBLEAdvertising() {
  // Extrae la parte BLE de tu antiguo setup() aquí
  Serial.println("\nEntrando en modo configuración BLE");
  BLEDevice::startAdvertising();
}

void setup() {
    Serial.begin(115200);
    prefs.begin("wifi", false);
    unsigned long t0 = millis();

    if (prefs.isKey("ssid") && prefs.isKey("pass")) {
      wifiSSID      = prefs.getString("ssid");
      wifiPassword  = prefs.getString("pass");
      Serial.println("Credenciales NVS halladas, conectando…");
      isSSIDReceived = isPasswordReceived = credentialsReceived = true;
      connectToWiFi();
    } else {
      Serial.println("Sin credenciales: esperando vía BLE");
      startBLEAdvertising();
    }

    while (!Serial && millis() - t0 < 3000);
    
    // Configuración del servo
    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);
    servo.setPeriodHertz(50);
    servo.attach(servoPin, 500, 2400);
    servo.attach(servoPin);

    // Configuración del botón
    pinMode(feedButton, INPUT_PULLUP);
    pinMode(resetButtonPin, INPUT_PULLUP);

    // Configuración BLE
    Serial.println("\nIniciando dispositivo BLE...");
    BLEDevice::init("ESP32-S3 WiFi Config");
    BLEServer *pServer = BLEDevice::createServer();
    BLEService *pService = pServer->createService(SERVICE_UUID);
    
    BLECharacteristic *pCharacteristicSSID = pService->createCharacteristic(
        CHARACTERISTIC_UUID_SSID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
    );
    
    BLECharacteristic *pCharacteristicPass = pService->createCharacteristic(
        CHARACTERISTIC_UUID_PASS,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
    );
    
    pCharacteristicSSID->setCallbacks(new MyCallbacks());
    pCharacteristicPass->setCallbacks(new MyCallbacks());
    
    pService->start();
    
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);
    BLEDevice::startAdvertising();
    
    Serial.println("Dispositivo BLE listo");
    Serial.println("Usa NRF Connect para enviar:");
    Serial.println("1. SSID a la característica SSID");
    Serial.println("2. Contraseña a la característica PASS");
}

void loop() {
    if (wifiConnected) {
        // Manejo de reconexión WiFi
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("Conexión WiFi perdida, reconectando...");
            wifiConnected = false;
            connectToWiFi();
        }
        
        // Manejo MQTT (no bloqueante)
        if (!client.connected()) {
            reconnectMqtt();
        }
        client.loop();

        unsigned long currentMillis = millis();
        if (isRotating) {
            if (currentMillis - lastRotationTime >= rotationTime) {
                currentRotations++;
                lastRotationTime = currentMillis;
                servo.writeMicroseconds(1700); // adelante
                Serial.println("Servo girando...");

                if (currentRotations >= targetRotations * 2) {
                    isRotating = false;
                    servo.writeMicroseconds(1500);
                    currentRotations = 0;
                    Serial.println("Rotaciones completadas");
                }
            }
        }
        int reading = digitalRead(feedButton);
        if (reading != lastButtonState) {
            lastDebounceTime = millis();
        }

        if ((millis() - lastDebounceTime) > debounceDelay) {
            if (reading != buttonState) {
                buttonState = reading;
                
                if (buttonState == LOW && !isRotating) {
                    targetRotations = 1;
                    isRotating = true;
                    currentRotations = 0;
                    rotationStartTime = millis();
                    servo.writeMicroseconds(1700);
                    Serial.println("Rotación iniciada por botón (1 vuelta)...");
                } else if (buttonState == LOW && isRotating) {
                    Serial.println("El servo ya está rotando. Espere a que termine.");
                }
            }
        }
        lastButtonState = reading;
    }
    yield();
    
    // ---------- BOTÓN DE RESET Wi‑Fi ----------
    static unsigned long resetPressStart = 0;
    const  unsigned long resetHoldTime   = 3000;

    if (digitalRead(resetButtonPin) == LOW) {
        if (resetPressStart == 0) resetPressStart = millis();

        if (millis() - resetPressStart >= resetHoldTime) {
            eraseCredentials();
        }
    } else {
        resetPressStart = 0;
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Mensaje recibido en el tema ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(message);

    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print("Error al deserializar JSON: ");
        Serial.println(error.c_str());
        return;
    }

    int id = doc["id"];
    targetRotations = doc["rotations"];

    Serial.print("ID: ");
    Serial.println(id);
    Serial.print("Rotaciones: ");
    Serial.println(targetRotations);

    if (id == 1 && !isRotating) {
        Serial.println("Ejecutando servo...");
        isRotating = true;
        currentRotations = 0;
        lastRotationTime = millis();
    } else if (id == 1 && isRotating) {
        Serial.println("Ya se está realizando una rotación.");
    }
}