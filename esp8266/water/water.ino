#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET    -1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define MOISTURE_SENSOR_PIN 34 // Soil Moisture Sensor Analog pin

// Calibration values
const int AIR_VALUE = 3100; // Replace 2900 with the value you got in air
const int WATER_VALUE = 2350; // Replace 1500 with the value you got in water

void setup() {
  Serial.begin(115200);
  
  // Initialize OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Check the display's I2C address
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.setTextSize(1); // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0,0); // Start at top-left corner
  display.display();
}

void loop() {
  int moistureLevel = analogRead(MOISTURE_SENSOR_PIN); // Read the moisture level
  Serial.println(moistureLevel); // Print the moisture level to the Serial Monitor

  // Map the moisture level from the sensor to a 0-100% scale
  int moisturePercent = map(moistureLevel, WATER_VALUE, AIR_VALUE, 100, 0);
  moisturePercent = constrain(moisturePercent, 0, 100); // Ensure the percentage is between 0 and 100
  
  // Display moisture percentage on OLED
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Moisture %: ");
  display.println(moisturePercent);
  display.display(); // Actually draw everything on the display

  delay(2000); // Wait for 2 seconds
}
