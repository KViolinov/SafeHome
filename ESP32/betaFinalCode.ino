#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

#define MOTION_SENSOR_PIN 13 

// Pin definitions for AI-Thinker model
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
#define Y3_GPIO_NUM      5
#define Y2_GPIO_NUM      4
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

// WiFi credentials
const char* ssid = "***"; // Replace with your WiFi SSID
const char* password = "******"; // Replace with your WiFi Password

// Firebase API variables
const char* firebaseAuth = "***********...";
const char* storageBucket = "*****"; // Firebase Storage bucket

void setup() {
  Serial.begin(115200);

  pinMode(MOTION_SENSOR_PIN, INPUT);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize the camera
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
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG; // JPEG format to minimize memory usage

  // Frame size and image quality settings
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10; // Higher quality if needed
  config.fb_count = 1;

  // Initialize the camera
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }
}

void loop() {
  // Capture a photo
  if (digitalRead(MOTION_SENSOR_PIN) == HIGH) {
    Serial.println("Motion detected!");

    // Capture a photo
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }
    

    // Upload image to Firebase
    sendImageToFirebase(fb->buf, fb->len);

    // Return the frame buffer to be reused
    esp_camera_fb_return(fb);

    // Debounce: avoid taking too many pictures in a short time
    delay(10000);  // Wait for 10 seconds before checking for motion again
  }
}

void sendImageToFirebase(uint8_t * imageData, size_t len) {
  HTTPClient http;

  String filename = "image_" + String(millis()) + ".jpg"; // Create a unique filename
  String url = "https://firebasestorage.googleapis.com/v0/b/" + String(storageBucket) + "/o/" + filename + "?uploadType=media";

  // Initialize HTTP request
  http.begin(url.c_str());
  http.addHeader("Authorization", "Bearer " + String(firebaseAuth));  // Use Bearer token for authentication
  http.addHeader("Content-Type", "image/jpeg");

  // Send the POST request with the image data
  int httpResponseCode = http.POST(imageData, len);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Image uploaded, response: " + response);
  } else {
    Serial.println("Error uploading image, HTTP response: " + String(httpResponseCode));
  }

  http.end();
}
