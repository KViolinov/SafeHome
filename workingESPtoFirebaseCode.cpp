#include <WiFi.h>
#include <FirebaseESP32.h>

// Network credentials
#define WIFI_SSID "B-Smart"
#define WIFI_PASSWORD "0889909595"

// Firebase project credentials
#define FIREBASE_HOST "https://safehome-c4576-default-rtdb.firebaseio.com"
#define FIREBASE_API_KEY "AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI"

// Firebase Authentication credentials
#define USER_EMAIL "kviolinov@gmail.com"
#define USER_PASSWORD "Kv0889909595"

// Createing an instance of the FirebaseData class
FirebaseData firebaseData;
FirebaseAuth auth;
FirebaseConfig config;

String getMacAddress() {
  uint8_t mac[6];
  char macStr[18];
  WiFi.macAddress(mac);
  snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(macStr);
}

void setup() {
  Serial.begin(115200);

  // Connecting to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connected to Wi-Fi");

  // Configure Firebase
  config.host = FIREBASE_HOST;
  config.api_key = FIREBASE_API_KEY;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  // Initialize Firebase
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Trying to sign in the user
  if (Firebase.signUp(&config, &auth, USER_EMAIL, USER_PASSWORD)) {
    Serial.println("Sign up succeeded");
  } else {
    if (config.signer.signupError.message == "EMAIL_EXISTS") {
      Serial.println("Email already exists. Assuming user is already authenticated.");
    } else {
      Serial.printf("Failed to sign up: %s\n", config.signer.signupError.message.c_str());
    }
  }
}

void loop() {
  // Generate a random integer
  int randomNumber = random(0, 100); // Random number between 0 and 99

  String macAddress = getMacAddress();

  // Create the Firebase path using the MAC address
  String firebasePath = "/" + macAddress + "/randomNumber";

  // Send the random number to Firebase
  if (Firebase.ready() && Firebase.setInt(firebaseData, firebasePath.c_str(), randomNumber)) {
    Serial.println("Data sent successfully");
  } else {
    Serial.print("Failed to send data: ");
    Serial.println(firebaseData.errorReason());
  }

  // Wait for 10 seconds
  delay(10000);
}
