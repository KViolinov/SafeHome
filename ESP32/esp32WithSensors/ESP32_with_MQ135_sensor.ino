#include <Arduino.h>

const int mq135Pin = 34; // Replace with your analog input pin
const int heaterPin = 25; // Replace with your digital output pin

void setup() {
  Serial.begin(115200);
  pinMode(heaterPin, OUTPUT);
  digitalWrite(heaterPin, HIGH); // Enable heater (check sensor datasheet)
}

void loop() {
  int sensorValue = analogRead(mq135Pin);
  // Process sensor value to get gas concentration (requires calibration)
  // ...

  Serial.print("MQ-135 Sensor Value: ");
  Serial.println(sensorValue);
  // Serial.print("Gas Concentration: ");
  // Serial.println(gasConcentration); // After calibration
  delay(1000);
}
