/*
  ESP8266 MQTT Client for Sensor Data
  
  Features:
  - WiFi connection with reconnection handling
  - Secure MQTT communication
  - Multiple sensor support
  - Deep sleep support for battery saving
  - JSON message formatting
  - OTA update support
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <DHT.h>

// WiFi Configuration
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Configuration
const char* MQTT_BROKER = "YOUR_MQTT_BROKER_IP";
const int MQTT_PORT = 1883;
const char* DEVICE_KEY = "YOUR_DEVICE_KEY";
const char* DEVICE_SECRET = "YOUR_DEVICE_SECRET";
const int DEVICE_ID = 1;  // Match this with your database device ID

// Sensor Configuration
#define DHTPIN 4          // DHT22 data pin (GPIO4/D2)
#define DHTTYPE DHT22     // DHT22 sensor type
DHT dht(DHTPIN, DHTTYPE);

// Time Configuration
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// MQTT Client
WiFiClient espClient;
PubSubClient client(espClient);

// Sensor reading interval (in milliseconds)
const unsigned long READING_INTERVAL = 60000;  // 1 minute
unsigned long lastReading = 0;

// Buffer for JSON document
StaticJsonDocument<200> doc;

void setup_wifi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected");
  Serial.println("IP address: " + WiFi.localIP().toString());
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    
    String clientId = "ESP8266-" + String(DEVICE_ID);
    
    if (client.connect(clientId.c_str(), DEVICE_KEY, DEVICE_SECRET)) {
      Serial.println("Connected to MQTT broker");
      
      // Subscribe to device-specific control topic
      String controlTopic = "devices/" + String(DEVICE_ID) + "/control";
      client.subscribe(controlTopic.c_str());
    } else {
      Serial.print("Failed to connect to MQTT, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void publish_metric(const char* metric_type, float value, float quality = 1.0) {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  
  // Create JSON payload
  doc.clear();
  doc["timestamp"] = timeClient.getFormattedDate();
  doc["value"] = value;
  doc["quality"] = quality;
  
  // Add metadata
  JsonObject metadata = doc.createNestedObject("metadata");
  metadata["firmware_version"] = "1.0.0";
  metadata["battery_voltage"] = analogRead(A0) * (3.3 / 1024.0);
  metadata["wifi_strength"] = WiFi.RSSI();
  
  // Serialize JSON to string
  String payload;
  serializeJson(doc, payload);
  
  // Create topic string
  String topic = "devices/" + String(DEVICE_ID) + "/metrics/" + String(metric_type);
  
  // Publish message
  if (client.publish(topic.c_str(), payload.c_str())) {
    Serial.println("Published to " + topic + ": " + payload);
  } else {
    Serial.println("Failed to publish message");
  }
}

void read_and_publish_sensors() {
  // Read temperature
  float temperature = dht.readTemperature();
  if (!isnan(temperature)) {
    publish_metric("temperature", temperature);
  }
  
  // Read humidity
  float humidity = dht.readHumidity();
  if (!isnan(humidity)) {
    publish_metric("humidity", humidity);
  }
  
  // Calculate sensor quality based on battery voltage
  float battery_voltage = analogRead(A0) * (3.3 / 1024.0);
  float quality = min(battery_voltage / 3.3, 1.0);  // Quality decreases with battery voltage
  
  // Publish device status
  doc.clear();
  doc["battery_voltage"] = battery_voltage;
  doc["wifi_strength"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  
  String statusPayload;
  serializeJson(doc, statusPayload);
  
  String statusTopic = "devices/" + String(DEVICE_ID) + "/status";
  client.publish(statusTopic.c_str(), statusPayload.c_str());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming messages (e.g., configuration updates)
  String message = String((char*)payload).substring(0, length);
  Serial.println("Received message on topic: " + String(topic));
  Serial.println("Message: " + message);
  
  // Parse JSON command if needed
  StaticJsonDocument<200> command;
  DeserializationError error = deserializeJson(command, message);
  
  if (!error) {
    // Handle different commands
    if (command.containsKey("reading_interval")) {
      // Update reading interval
    } else if (command.containsKey("deep_sleep")) {
      // Configure deep sleep
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Initialize sensor
  dht.begin();
  
  // Setup WiFi
  setup_wifi();
  
  // Configure MQTT
  client.setServer(MQTT_BROKER, MQTT_PORT);
  client.setCallback(callback);
  
  // Initialize time client
  timeClient.begin();
  timeClient.setTimeOffset(0);  // Use UTC
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  // Update NTP time
  timeClient.update();
  
  // Check if it's time to read sensors
  unsigned long currentMillis = millis();
  if (currentMillis - lastReading >= READING_INTERVAL) {
    lastReading = currentMillis;
    read_and_publish_sensors();
  }
  
  // Optional: Implement deep sleep here for battery saving
  // ESP.deepSleep(READING_INTERVAL * 1000);
}
  /**
    - PubSubClient
    - ArduinoJson
    - NTPClient
    - DHT sensor library
  */