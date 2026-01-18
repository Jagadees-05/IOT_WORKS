#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

/* -------- WiFi -------- */
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

/* -------- MQTT -------- */
const char* mqtt_server = "BROKER_IP";
const int mqtt_port = 1883;
const char* topic = "esp32/ldr";

/* -------- LDR -------- */
#define LDR_PIN 34
#define LIGHT_THRESHOLD 2000   // Tune this properly

WiFiClient espClient;
PubSubClient client(espClient);

/* -------- Functions -------- */
void connectWiFi();
void reconnectMQTT();

void setup() {
  Serial.begin(115200);
  pinMode(LDR_PIN, INPUT);

  connectWiFi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  int adcValue = analogRead(LDR_PIN);

  const char* state = (adcValue > LIGHT_THRESHOLD) ? "LIGHT" : "DARK";

  StaticJsonDocument<100> doc;
  doc["adc"] = adcValue;
  doc["state"] = state;

  char payload[100];
  serializeJson(doc, payload);

  client.publish(topic, payload);

  Serial.println(payload);

  delay(2000);
}

/* -------- WiFi -------- */
void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

/* -------- MQTT -------- */
void reconnectMQTT() {
  while (!client.connected()) {
    if (client.connect("ESP32_LDR")) {
      // connected
    } else {
      delay(2000);
    }
  }
}
