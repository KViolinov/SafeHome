#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <EEPROM.h>

const char* apSSID = "ESP32-Access-Point";  // Access Point SSID
const char* apPassword = "123456789";       // Access Point Password

const int EEPROM_SIZE = 64;  // Size for storing SSID and Password in EEPROM
WebServer server;
bool wifiConnected = false;

WiFiUDP udp;
const char* udpAddress = "255.255.255.255";  // Broadcast address
const int udpPort = 5005;
bool discovered = false;  // Flag to stop sending once discovered

void setup() {
  Serial.begin(115200);
  EEPROM.begin(EEPROM_SIZE);

  // Load Wi-Fi credentials from EEPROM and attempt to connect
  String storedSSID = loadSSIDFromEEPROM();
  String storedPassword = loadPasswordFromEEPROM();

  if (storedSSID.length() > 0 && storedPassword.length() > 0) {
    Serial.println("Attempting to connect with stored credentials...");
    WiFi.begin(storedSSID.c_str(), storedPassword.c_str());
    wifiConnected = attemptWiFiConnection(10000);  // 10-second timeout
  }

  if (wifiConnected) {
    printWiFiDetails(); // Print Wi-Fi details when connected
  } else {
    // Start Access Point if connection fails
    startAccessPoint();
  }

  // Serve web page for Wi-Fi configuration
  server.on("/", handleRoot);
  server.on("/submit", HTTP_POST, handleSubmit);
  server.begin();
  Serial.println("HTTP server started.");

  // Start UDP
  udp.begin(udpPort);
}

void loop() {
  // Handle web server requests
  server.handleClient();

  // Broadcast UDP message if not discovered
  if (!discovered && wifiConnected) {
    // Get MAC address
    String macAddress = WiFi.macAddress();

    // Construct message with "ESP32_PACKAGE" and MAC address
    String message = "ESP32_PACKAGE " + macAddress;

    // Send UDP broadcast message
    udp.beginPacket(udpAddress, udpPort);
    udp.print(message);
    udp.endPacket();

    Serial.println("Sent UDP message: " + message);

    // Listen for response
    int packetSize = udp.parsePacket();
    if (packetSize) {
      char incomingPacket[255];
      int len = udp.read(incomingPacket, 255);
      if (len > 0) {
        incomingPacket[len] = '\0';
      }

      Serial.printf("Received UDP response: %s\n", incomingPacket);

      // If the response is "DISCOVERED", stop sending packages
      if (String(incomingPacket) == "DISCOVERED") {
        Serial.println("Device discovered by the server. Stopping broadcast.");
        discovered = true;  // Set flag to stop sending further packages
      }
    }

    // Wait before sending the next package
    delay(5000);
  }
}

// Function to handle root URL for Wi-Fi configuration
void handleRoot() {
  String html = "<html><body><h1>ESP32 WiFi Configuration</h1>";
  html += "<form action=\"/submit\" method=\"POST\">";
  html += "SSID: <input type=\"text\" name=\"ssid\"><br>";
  html += "Password: <input type=\"password\" name=\"password\"><br>";
  html += "<input type=\"submit\" value=\"Submit\">";
  html += "</form></body></html>";

  server.send(200, "text/html", html);
}

// Function to handle form submission
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

// Function to print connected Wi-Fi details
void printWiFiDetails() {
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("Connected SSID: ");
  Serial.println(WiFi.SSID());  // Print the SSID
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// Function to start Access Point
void startAccessPoint() {
  WiFi.softAP(apSSID, apPassword);
  Serial.println("Access Point started.");
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
}
