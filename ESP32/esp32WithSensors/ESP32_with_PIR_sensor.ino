const int PIR_SENSOR_PIN = 2; // Replace with the actual pin connected to the PIR sensor

void setup() {
  Serial.begin(9600);
  pinMode(PIR_SENSOR_PIN, INPUT);
}

void loop() {
  int sensorVal = digitalRead(PIR_SENSOR_PIN);
  if (sensorVal == HIGH) {
    Serial.println("Motion Detected");
  }
  else{
    Serial.println("not detected");
  }
  delay(1000); // Adjust delay as needed
}
