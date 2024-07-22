#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHTPIN D2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

ESP8266WebServer server(80);

const char* ssid = "BAS-Students";
const char* password = "BaseWiFi4Students";

// Function to display the sensor readings on the web server
void handleRoot() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  String message = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">";
  message += "<title>Weather Information</title>";
  message += "<style>body { font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background-color: #f0f0f0; }";
  message += "h1 { color: #333; }";
  message += "p { font-size: 24px; color: #666; }";
  message += ".container { background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }";
  message += "</style></head><body>";
  message += "<div class=\"container\"><h1>Weather Station</h1>";
  message += "<p>Temperature: " + String(t) + " &deg;C</p>";
  message += "<p>Humidity: " + String(h) + "%</p></div>";
  message += "<script>setTimeout(function(){ window.location.reload(1); }, 10000);</script>"; // Auto-refresh every 10 seconds
  message += "</body></html>";

  server.send(200, "text/html", message);
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
  dht.begin();

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();

  static unsigned long lastTime = 0;
  unsigned long currentTime = millis();
  if (currentTime - lastTime > 2000) {
    lastTime = currentTime;
    
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;

      float h = dht.readHumidity();
      float t = dht.readTemperature();

      if (!isnan(h) && !isnan(t)) {
        String postData = "{\"temperature\":" + String(t) + ",\"humidity\":" + String(h) + "}";
        
        // Updated begin method call
        http.begin(client, "http://193.168.173.216:5000/update_sensor_data");
        
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0) {
          String response = http.getString();
          Serial.println(response);
        } else {
          Serial.print("Error on sending POST: ");
          Serial.println(httpResponseCode);
        }
        http.end();
      }
    }
  }
}
