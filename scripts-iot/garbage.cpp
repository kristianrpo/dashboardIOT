#include <WiFi.h>
#include <HTTPClient.h>

// Credenciales WiFi
const char* ssid = "Sala de Juntas";
const char* password = "";

// URL del servidor donde se enviarán los datos
const char* serverUrl = "https://dashboard.cteisabaneta.space/api/garbage/save/";


// Pines del sensor HC-SR04 para MEDICAMENTOS VENCIDOS
const int trigPinM = 22;
const int echoPinM = 23;

// Pines de salida para lEDA y lEDAE
const int pinLEDA = 19;   // Pin para lEDA
const int pinLEDAE = 18;  // Pin para lEDAE

// Pin para monitorear la conexión a internet (pin 35)
const int pinInternet = 2;


// Función para medir la distancia
float medirDistancia(int trigPin, int echoPin) {
    const int numLecturas = 5;
    float distanciaTotal = 0;
    int lecturasValidas = 0;

    for (int i = 0; i < numLecturas; i++) {
        digitalWrite(trigPin, LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin, HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin, LOW);

        long duracion = pulseIn(echoPin, HIGH);

        if (duracion > 0) {
            float distancia = duracion * 0.034 / 2;
            distanciaTotal += distancia;
            lecturasValidas++;
        }
        delay(50);
    }
    float total = distanciaTotal / lecturasValidas;
    if (total >= 100) {
        total = 100;
    }

    return (lecturasValidas > 0) ? total : -1;
}

void setup() {
    Serial.begin(9600);
    
    // Configurar pines de los sensores Ultrasonido
    pinMode(trigPinM, OUTPUT);
    pinMode(echoPinM, INPUT);
    
    // Configurar pines de salida para lEDA y lEDAE
    pinMode(pinLEDA, OUTPUT);
    pinMode(pinLEDAE, OUTPUT);

    // Configurar pin 35 como salida para el estado de la conexión a internet
    pinMode(pinInternet, OUTPUT);

    WiFi.begin(ssid, password);
    Serial.print("Conectando a WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConectado a WiFi");
}

void loop() {
    // Verificar el estado de la conexión WiFi
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Conexión a internet activa.");
        digitalWrite(pinInternet, HIGH); // Encender el pin 35 si hay conexión
    } else {
        Serial.println("Error: No conectado a WiFi");
        digitalWrite(pinInternet, LOW); // Apagar el pin 35 si no hay conexión
    }

    // Medir la distancia
    float distanciaM = medirDistancia(trigPinM, echoPinM);
  // Control de lEDA y lEDAE según la distancia
  
  { if (distanciaM >= 20.0) {
      
         digitalWrite(pinLEDA, HIGH);
         digitalWrite(pinLEDAE, LOW);
      delay(1000);
    } else {
        
        digitalWrite(pinLEDA, LOW);
        digitalWrite(pinLEDAE, HIGH);
      delay(1000);
    }

    Serial.print("Distancia MEDICAMENTOS: ");
    Serial.println(distanciaM);

  }

    // Enviar datos al servidor si hay conexión a internet
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");

        // Crear el JSON con los valores
        String jsonPayload = "{";
        jsonPayload += "\"raae_distance\": 100, ";
        jsonPayload += "\"caps_distance\": 100, ";
        jsonPayload += "\"luminaires_distance\": 100, ";
        jsonPayload += "\"batteries_distance\": 100, ";
        jsonPayload += "\"medicines_distance\": " + String(distanciaM) + ", ";
        jsonPayload += "\"oils_distance\": 100";
        jsonPayload += "}";

        int httpResponseCode = http.POST(jsonPayload);

        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);

        http.end();
    }

    delay(10000); // Esperar 10 segundos antes de la siguiente lectura
}