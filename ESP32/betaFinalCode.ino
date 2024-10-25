/* not tested final code with FreeRTOS-AP-UDP-Live video stream */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <EEPROM.h>
#include <WiFiUdp.h>
#include <FirebaseESP32.h> // Firebase library
#include <DHT.h>

// Camera and sensor pin configuration
#define PWDN_GPIO_NUM    -1
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM    21
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      19
#define Y4_GPIO_NUM      18
#define Y3_GPIO_NUM       5
#define Y2_GPIO_NUM       4
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

#define DHT_PIN 13
#define FIRE_SENSOR_PIN 14
#define MQ135_PIN 15
#define PIR_PIN 16

const char* apSSID = "ESP32-Access-Point";
const char* apPassword = "123456789";
const int EEPROM_SIZE = 64;
WebServer server(80);
WiFiUDP udp;
bool wifiConnected = false;
bool discovered = false;
TaskHandle_t sensorTaskHandle;
TaskHandle_t pirTaskHandle;

// Firebase setup
#define FIREBASE_HOST "YOUR_FIREBASE_HOST"
#define FIREBASE_AUTH "YOUR_FIREBASE_AUTH_TOKEN"
FirebaseData fbData;

esp_err_t init_camera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;  // 20MHz for better performance
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;  // 640x480 resolution
    config.jpeg_quality = 12;  // Medium quality for better balance
    config.fb_count = 2;  // Frame buffers

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init FAIL: 0x%x", err);
        return err;
    }
    Serial.println("Camera init OK");
    return ESP_OK;
}


void setup() {
    Serial.begin(115200);
    EEPROM.begin(EEPROM_SIZE);
    
    // Load Wi-Fi credentials from EEPROM and attempt to connect
    String storedSSID = loadSSIDFromEEPROM();
    String storedPassword = loadPasswordFromEEPROM();
    if (storedSSID.length() > 0 && storedPassword.length() > 0) {
        WiFi.begin(storedSSID.c_str(), storedPassword.c_str());
        wifiConnected = attemptWiFiConnection(10000);
    }

    if (wifiConnected) {
        printWiFiDetails();
    } else {
        startAccessPoint();
    }

    init_camera();
    server.on("/", handleRoot);
    server.on("/video", handleVideoStream);
    server.on("/submit", HTTP_POST, handleSubmit);
    server.begin();
    udp.begin(5005);
    
    // Firebase and tasks setup
    Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
    xTaskCreatePinnedToCore(checkSensors, "SensorTask", 4096, NULL, 1, &sensorTaskHandle, 1);
    xTaskCreatePinnedToCore(checkPIRSensor, "PIRTask", 4096, NULL, 1, &pirTaskHandle, 1);
}

void loop() {
    server.handleClient();

    if (discovered && wifiConnected) {
        handleVideoStream();
    }

    if (!discovered && wifiConnected) {
        String message = "ESP32_PACKAGE " + WiFi.macAddress();
        udp.beginPacket("255.255.255.255", 5005);
        udp.print(message);
        udp.endPacket();
        Serial.println("Sent UDP message: " + message);

        int packetSize = udp.parsePacket();
        if (packetSize) {
            char incomingPacket[255];
            int len = udp.read(incomingPacket, 255);
            if (len > 0) incomingPacket[len] = '\0';

            if (String(incomingPacket) == "DISCOVERED") {
                Serial.println("Device discovered by the server. Stopping broadcast.");
                discovered = true;
            }
        }
        delay(5000);
    }
}

void checkSensors(void *parameter) {
    const int DHT_THRESHOLD = 50;
    const int FIRE_THRESHOLD = HIGH;  // Set to HIGH if you want alert only on HIGH reading
    const int MQ135_THRESHOLD = 50;

    String lastStatus = ""; // Store last status to prevent duplicate Firebase writes

    while (true) {
        // Read sensor values
        int dhtValue = analogRead(DHT_PIN);
        int fireValue = digitalRead(FIRE_SENSOR_PIN);
        int mq135Value = analogRead(MQ135_PIN);

        // Determine the alert status based on sensor values
        String status;
        if (dhtValue > DHT_THRESHOLD) {
            status = "Alert! DHT Sensor is above normal.";
        } else if (fireValue == FIRE_THRESHOLD) {
            status = "Alert! Fire Sensor is above normal.";
        } else if (mq135Value > MQ135_THRESHOLD) {
            status = "Alert! Air quality sensor is above normal.";
        } else {
            status = "All sensors within normal range.";
        }

        // Only update Firebase if the status has changed
        if (status != lastStatus) {
            bool success = Firebase.setString(fbData, "/sensors/status", status);
            if (success) {
                Serial.println("Firebase update successful: " + status);
                lastStatus = status; // Update last status to prevent duplicates
            } else {
                Serial.println("Failed to update Firebase.");
            }
        }

        vTaskDelay(10000 / portTICK_PERIOD_MS);  // Delay for 10 seconds
    }
}


void checkPIRSensor(void *parameter) {
    while (true) {
        if (digitalRead(PIR_PIN) == HIGH) {
            camera_fb_t * fb = esp_camera_fb_get();
            if (fb) {
                sendImageToFirebase(fb->buf, fb->len);
                esp_camera_fb_return(fb);
            }
            delay(10000);
        }
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}

/* Firebase Image Upload */
void sendImageToFirebase(uint8_t * imageData, size_t len) {
    HTTPClient http;
    String url = "https://firebasestorage.googleapis.com/v0/b/YOUR_PROJECT_ID/o/image_" + String(millis()) + ".jpg?uploadType=media";
    http.begin(url.c_str());
    http.addHeader("Authorization", "Bearer YOUR_FIREBASE_AUTH_TOKEN");
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(imageData, len);
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Image uploaded, response: " + response);
    } else {
        Serial.println("Error uploading image, HTTP response: " + String(httpResponseCode));
    }
    http.end();
}

void handleRoot() {
    String html = "<html><body><h1>ESP32 WiFi Configuration</h1>";
    html += "<form action=\"/submit\" method=\"POST\">";
    html += "SSID: <input type=\"text\" name=\"ssid\"><br>";
    html += "Password: <input type=\"password\" name=\"password\"><br>";
    html += "<input type=\"submit\" value=\"Submit\">";
    html += "</form></body></html>";
    server.send(200, "text/html", html);
}

void handleVideoStream() {
    camera_fb_t * fb = NULL;
    char part_buf[64];

    server.setContentLength(CONTENT_LENGTH_UNKNOWN);
    server.send(200, "multipart/x-mixed-replace; boundary=frame");

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Camera capture failed");
            break;
        }

        snprintf(part_buf, 64, "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
        server.sendContent(part_buf);
        server.sendContent((const char*)fb->buf, fb->len);
        server.sendContent("\r\n");

        esp_camera_fb_return(fb);

        if (!server.client().connected()) {
            break;
        }

        delay(33);  // Adjust delay for ~30fps (1000ms / 30fps ≈ 33ms)
    }
}

void handleSubmit() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");

    // Save SSID and Password to EEPROM
    saveCredentialsToEEPROM(ssid, password);

    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);

    // Attempt to connect to the specified Wi-Fi network
    WiFi.begin(ssid.c_str(), password.c_str());
    wifiConnected = attemptWiFiConnection(10000);  // 10-second timeout

    if (wifiConnected) {
        printWiFiDetails(); // Print Wi-Fi details when connected
        server.send(200, "text/html", "Connected to Wi-Fi! ESP32 will restart now.");
    } else {
        Serial.println("Failed to connect. Reverting to AP mode.");
        server.send(200, "text/html", "Failed to connect. Please try again.");
    }

    delay(2000);
    ESP.restart();  // Restart the ESP32 to try connecting again with new credentials
}

// Function to save SSID and Password to EEPROM
void saveCredentialsToEEPROM(const String& ssid, const String& password) {
    for (int i = 0; i < EEPROM_SIZE; i++) {
        EEPROM.write(i, 0); // Clear EEPROM
    }

    for (int i = 0; i < ssid.length(); i++) {
        EEPROM.write(i, ssid[i]); // Save SSID
    }
    EEPROM.write(ssid.length(), '\0');  // Null terminate SSID

    for (int i = 0; i < password.length(); i++) {
        EEPROM.write(32 + i, password[i]);  // Save Password starting from index 32
    }
    EEPROM.write(32 + password.length(), '\0');  // Null terminate Password

    EEPROM.commit();
}

// Function to load SSID from EEPROM
String loadSSIDFromEEPROM() {
    char ssid[32];
    for (int i = 0; i < 32; i++) {
        ssid[i] = EEPROM.read(i);
    }
    return String(ssid);
}

// Function to load Password from EEPROM
String loadPasswordFromEEPROM() {
    char password[32];
    for (int i = 0; i < 32; i++) {
        password[i] = EEPROM.read(32 + i);
    }
    return String(password);
}

// Function to print Wi-Fi details
void printWiFiDetails() {
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("Connected to WiFi. SSID: ");
    Serial.println(WiFi.SSID());
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}

// Function to attempt Wi-Fi connection with a timeout
bool attemptWiFiConnection(unsigned long timeout) {
    unsigned long startAttemptTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout) {
        delay(100);
        Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to Wi-Fi!");
    return true;
  } else {
    Serial.println("\nFailed to connect.");
    return false;
  }
}

// Function to start Access Point mode
void startAccessPoint() {
    WiFi.softAP(apSSID, apPassword);
    Serial.println("Access Point started. Connect to: " + String(apSSID));
    Serial.print("IP Address: ");
    Serial.println(WiFi.softAPIP());
}
