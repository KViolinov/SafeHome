#define RED_PIN    25
#define GREEN_PIN  26
#define BLUE_PIN   27
#define RELAY_PIN  14

// Task to control the RGB LED
void TaskRGB(void *pvParameters) {
  (void) pvParameters;
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  while (1) {
    // Set RGB to red
    analogWrite(RED_PIN, 255);
    analogWrite(GREEN_PIN, 0);
    analogWrite(BLUE_PIN, 0);
    vTaskDelay(1000 / portTICK_PERIOD_MS);

    // Set RGB to green
    analogWrite(RED_PIN, 0);
    analogWrite(GREEN_PIN, 255);
    analogWrite(BLUE_PIN, 0);
    vTaskDelay(1000 / portTICK_PERIOD_MS);

    // Set RGB to blue
    analogWrite(RED_PIN, 0);
    analogWrite(GREEN_PIN, 0);
    analogWrite(BLUE_PIN, 255);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

// Task to control the relay
void TaskRelay(void *pvParameters) {
  (void) pvParameters;
  pinMode(RELAY_PIN, OUTPUT);

  while (1) {
    // Turn relay on
    digitalWrite(RELAY_PIN, HIGH);
    vTaskDelay(3500 / portTICK_PERIOD_MS);

    // Turn relay off
    digitalWrite(RELAY_PIN, LOW);
    vTaskDelay(2300 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);
  xTaskCreate(TaskRGB, "Task RGB", 1000, NULL, 1, NULL);
  xTaskCreate(TaskRelay, "Task Relay", 1000, NULL, 1, NULL);
}

void loop() {
  // Empty. Tasks are running independently.
}
