#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <DNSServer.h>
#include <LittleFS.h>

#define DHTPIN D4
#define DHTTYPE DHT11
#define DEVICE_ID "DHT11-SC-E01"
#define SECRET_KEY "3e74c52a0d8f796057fe7564289665ac"

DHT dht(DHTPIN, DHTTYPE);
const char* serverUrl = "http://10.42.0.1:5001/update_sensor_data";
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 3600, 60000);
ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);
  if (!LittleFS.begin()) {
    Serial.println("An Error has occurred while mounting LittleFS");
    return;
  }
  File credFile = LittleFS.open("/credentials.txt", "r");
  if (!credFile) {
    Serial.println("Failed to open credentials file");
    startAPMode();
    return;
  }
  String ssid = credFile.readStringUntil('\n');
  ssid.trim();
  String password = credFile.readStringUntil('\n');
  password.trim();
  credFile.close();

  WiFi.begin(ssid.c_str(), password.c_str());
  Serial.print("Connecting to WiFi");

  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 10000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect, switching to AP mode");
    startAPMode();
  } else {
    Serial.println("\nWiFi connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  }

  dht.begin();
  timeClient.begin();
}

void startAPMode() {
  const char *apSSID = "ESP8266-Config";
  WiFi.softAP(apSSID);

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", configPageHTML());
  });

  server.on("/config", HTTP_POST, []() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    File credFile = LittleFS.open("/credentials.txt", "w");
    credFile.println(ssid);
    credFile.println(password);
    credFile.close();
    WiFi.begin(ssid.c_str(), password.c_str());
    server.send(200, "text/html", "<p>Configuration saved. Please reset the device to apply settings.</p>");
  });

  server.begin();
  Serial.println("AP Mode. Connect to Wi-Fi network " + String(apSSID) + " and access http://192.168.4.1 to configure Wi-Fi.");
}

String configPageHTML() {
  int n = WiFi.scanNetworks();
  String form = "<!DOCTYPE html><html><head><style>";
  form += "body {font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;}";
  form += "div {width: 300px; padding: 20px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); text-align: center; background-color: #f1f1f1;}";
  form += "select, input[type='password'], input[type='submit'] {width: 100%; padding: 10px; margin-top: 8px; margin-bottom: 16px; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}";
  form += "input[type='submit'] {background-color: #4CAF50; color: white; border: none; cursor: pointer;}";
  form += "input[type='submit']:hover {background-color: #45a049;}";
  form += "</style></head><body><div>";
  form += "<h3>Select Wi-Fi Network</h3><form action='/config' method='POST'>";
  form += "SSID: <select name='ssid'>";

  for (int i = 0; i < n; ++i) {
    form += "<option value='" + WiFi.SSID(i) + "'>" + WiFi.SSID(i) + " (" + WiFi.RSSI(i) + " dBm)</option>";
  }

  form += "</select><br>Password: <input type='password' name='password'><br><input type='submit' value='Connect'>";
  form += "</form><footer>Designed by: Eng. Maitham Al-rubaye<br>Supervised by: Dr. Atakan Aral<br>University of Vienna<br>2024</footer></div></body></html>";
  return form;
}

void loop() {
  server.handleClient();
  static unsigned long lastTime = 0;
  unsigned long currentTime = millis();
  if (currentTime - lastTime > 30000) {
    lastTime = currentTime;
    timeClient.update();
    if (WiFi.status() == WL_CONNECTED) {
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();
      String postData = "{\"temperature\":" + String(temperature) + ",\"humidity\":" + String(humidity) + ",\"timestamp\":\"" + timeClient.getFormattedTime() + "\"}";
      WiFiClient client;
      HTTPClient http;
      http.begin(client, serverUrl);
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(postData);
      
      if (httpResponseCode > 0) {
        Serial.println(http.getString());
      } else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
      }
      http.end();
    }
  }
}
