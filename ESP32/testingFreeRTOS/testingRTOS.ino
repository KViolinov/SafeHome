#include <Arduino.h>
#include <FreeRTOS.h>
#include <ESP32Servo.h>

// Define the RGB LED pins
#define RED_PIN 5
#define GREEN_PIN 18
#define BLUE_PIN 19

// Define the Servo pin
#define SERVO_PIN 26

// Create a Servo object
Servo myServo;

// Task handles
TaskHandle_t TaskHandleRGB;
TaskHandle_t TaskHandleServo;

void setup() {
  Serial.begin(115200);
  
  // Initialize the RGB LED pins as outputs
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // Attach the servo to the specified pin
  myServo.attach(SERVO_PIN);
  
  // Create tasks
  xTaskCreate(taskControlRGB, "ControlRGB", 1024, NULL, 1, &TaskHandleRGB);
  xTaskCreate(taskControlServo, "ControlServo", 1024, NULL, 1, &TaskHandleServo);
}

void loop() {
  // Nothing to do here, everything is handled by tasks
}

// Task to control the RGB LED
void taskControlRGB(void *pvParameters) {
  while (1) {
    // Red
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // Green
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, LOW);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // Blue
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, HIGH);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // Yellow
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, LOW);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // Cyan
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // Magenta
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, HIGH);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // White
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    
    // Off
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

// Task to control the servo motor
void taskControlServo(void *pvParameters) {
  while (1) {
    for (int pos = 0; pos <= 180; pos += 1) {
      myServo.write(pos);
      vTaskDelay(15 / portTICK_PERIOD_MS);
    }
    for (int pos = 180; pos >= 0; pos -= 1) {
      myServo.write(pos);
      vTaskDelay(15 / portTICK_PERIOD_MS);
    }
  }
}
