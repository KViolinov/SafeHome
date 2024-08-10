#include <WiFi.h>
#include <Firebase_ESP_Client.h>
//#include <Firebase_ESP_WiFi_Manager.h>
#include <ArduinoJson.h>
#include <camera_fb.h>
#include <WiFiManager.h> // Example using ESP32 WiFi Manager
#include <Firebase_Arduino.h>

// Replace with your network credentials and Firebase configuration
const char* ssid = "B-Smart";
const char* password = "0889909595";
FirebaseData firebaseData;
FirebaseAuth firebaseAuth;

// Replace with your Firebase configuration
FirebaseConfig config;
#define FIREBASE_HOST "https://safehome-c4576-default-rtdb.firebaseio.com"
#define API_KEY "AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI"
#define AUTH_DOMAIN "safehome-c4576.firebaseapp.com"
#define DATABASE_URL "https://safehome-c4576-default-rtdb.firebaseio.com"
#define STORAGE_BUCKET "safehome-c4576.appspot.com"

// Camera configuration
#define CAMERA_MODEL ESP32_CAM_OV2640
#define PCLK 12000000
#define PIXFORMAT RGB565
#define FRAMESIZE UXGA
#define JPEG_QUALITY 85

// Function to initialize WiFi and Firebase
void initFirebase() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");

  config.wifi_ssid = ssid;
  config.wifi_password = password;
  config.api_key = API_KEY;
  config.auth_domain = AUTH_DOMAIN;
  config.database_url = DATABASE_URL;
  config.storage_bucket = STORAGE_BUCKET;

  Firebase.begin(&config, &firebaseAuth);
}

void setup() {
  Serial.begin(115200);

  // WiFi configuration using WiFiManager
  WiFiManager wifiManager;
  wifiManager.autoConnect("MyWiFiAP");

  // Firebase initialization
  Firebase.begin(firebaseConfig);
  
  // Initialize camera
  camera_fb_init();
  camera_fb_config(CAMERA_MODEL, PCLK, PIXFORMAT, FRAMESIZE, JPEG_QUALITY);

  initFirebase();
}

void loop() {
  // Capture image
  camera_fb_t * fb = camera_fb_get();
  if (!fb) {
    Serial.println("Error capturing frame");
    return;
  }

  // Create Firebase storage reference
  String path = "/images/" + String(millis()) + ".jpg";
  FirebaseStorage storage = Firebase.storage();

  // Upload image to Firebase
  if (storage.putData(path, fb->len, (const uint8_t *)fb->buf)) {
    Serial.println("Image uploaded successfully");
  } else {
    Serial.println("Error uploading image");
    Serial.println(storage.errorDetails());
  }

  camera_fb_return(fb);
  delay(10000); // Capture image every 10 seconds
}
