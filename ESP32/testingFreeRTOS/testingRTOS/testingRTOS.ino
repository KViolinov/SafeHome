#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>

// Pin Definitions
#define DHTPIN 4        // DHT11 data pin
#define DHTTYPE DHT11   // DHT 11
#define MQ135_PIN 34    // MQ135 sensor analog pin
#define FIRE_SENSOR_PIN 35 // Fire sensor analog pin
#define PIR_SENSOR_PIN 33 // PIR sensor digital pin
#define LED_PIN 15      // RGB LED pin

// OLED Display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_I2C_ADDRESS 0x3C // Typical I2C address for SSD1306

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// DHT11 Sensor
DHT dht(DHTPIN, DHTTYPE);

// Wi-Fi Credentials
const char* ssid = "B-Smart";
const char* password = "0889909595";

// FreeRTOS Task Handles
TaskHandle_t WiFiTaskHandle;
TaskHandle_t SensorTaskHandle;
TaskHandle_t DisplayTaskHandle;

// Variables for Sensor Data
bool isConnectedToWiFi = false;
bool isSensorTriggered = false;
String sensorMessage = "";

void setup() {
  // Start Serial Monitor
  Serial.begin(115200);

  // Initialize DHT11
  dht.begin();

  // Initialize OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.display();

  // Initialize RGB LED
  pinMode(LED_PIN, OUTPUT);

  // Create Tasks
  xTaskCreate(WiFiTask, "WiFi Task", 4096, NULL, 1, &WiFiTaskHandle);
  xTaskCreate(SensorTask, "Sensor Task", 4096, NULL, 1, &SensorTaskHandle);
  xTaskCreate(DisplayTask, "Display Task", 4096, NULL, 1, &DisplayTaskHandle);
}

void loop() {
  // Let FreeRTOS handle the tasks
}

void WiFiTask(void * pvParameters) {
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  isConnectedToWiFi = true;
  sensorMessage = "Connected to WiFi";
  Serial.println(sensorMessage);
  
  vTaskDelete(NULL); // Delete this task after Wi-Fi is connected
}

void SensorTask(void * pvParameters) {
  while (1) {
    // Read DHT11 Sensor
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("Failed to read from DHT sensor!");
    }

    // Read MQ135 Sensor
    int mq135_value = analogRead(MQ135_PIN);
    if (mq135_value > 400) {  // Threshold value, adjust as needed
      isSensorTriggered = true;
      sensorMessage = "Gas Detected!";
      Serial.println(sensorMessage);
    }

    // Read Fire Sensor
    int fire_value = analogRead(FIRE_SENSOR_PIN);
    if (fire_value < 300) {  // Threshold value, adjust as needed
      isSensorTriggered = true;
      sensorMessage = "Fire Detected!";
      Serial.println(sensorMessage);
    }

    // Read PIR Sensor
    int pir_state = digitalRead(PIR_SENSOR_PIN);
    if (pir_state == HIGH) {
      isSensorTriggered = true;
      sensorMessage = "Motion Detected!";
      Serial.println(sensorMessage);
    }

    // Delay before the next check
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void DisplayTask(void * pvParameters) {
  while (1) {
    display.clearDisplay();
    
    if (isConnectedToWiFi) {
      display.setTextSize(1);
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 0);
      display.println("Connected to WiFi");
    }
    
    if (isSensorTriggered) {
      display.setTextSize(1);
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 10);
      display.println(sensorMessage);
      
      // Turn on LED if any sensor is triggered
      digitalWrite(LED_PIN, HIGH);
      isSensorTriggered = false;  // Reset after handling
    } else {
      digitalWrite(LED_PIN, LOW); // Turn off LED if no sensor is triggered
    }

    display.display();

    // Delay before the next update
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

