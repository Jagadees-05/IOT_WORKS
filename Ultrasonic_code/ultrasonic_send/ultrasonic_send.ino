#include <WiFi.h>
#include <PubSubClient.h>

// -------- WiFi Credentials --------
const char* ssid = "Jaga's";
const char* password = "naathaaa";

// -------- MQTT Broker --------
const char* mqtt_server = "broker.emqx.io";
const char* mqtt_topic  = "esp32/ultrasonic";

// -------- Ultrasonic Pins --------
#define TRIG_PIN 5
#define ECHO_PIN 18

WiFiClient espClient;
PubSubClient client(espClient);

long duration;
float distance;

// ---------- WiFi Connect ----------
void setup_wifi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");
}

// ---------- MQTT Reconnect ----------
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Client")) {
      Serial.println("Connected");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

// ---------- Loop ----------
void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Trigger ultrasonic
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30 ms timeout

  // Distance calculation
  distance = (duration * 0.034) / 2;

  // JSON payload
  String payload = "{";
  payload += "\"distance_cm\":";
  payload += String(distance, 2);
  payload += "}";

  // Publish to MQTT
  client.publish(mqtt_topic, payload.c_str());

  // Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  Serial.println("MQTT Sent:");
  Serial.println(payload);
  Serial.println("--------------------");

  delay(1000);
}
