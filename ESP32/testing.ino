#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include "soc/soc.h" // Disable brownout problems
#include "soc/rtc_cntl_reg.h" // Disable brownout problems

// Configuration for AI Thinker Camera board
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

const char* ssid     = "Konstantin's P60 Pro"; // CHANGE HERE
const char* password = "0889909595"; // CHANGE HERE

WebServer server(80);  // Create a web server on port 80

// Function to initialize the camera
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

    // Set to 480p
    config.frame_size = FRAMESIZE_VGA;  // 640x480 resolution
    config.jpeg_quality = 12;  // Medium quality for better balance
    config.fb_count = 2;  // Frame buffers

    // Camera initialization
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init FAIL: 0x%x", err);
        return err;
    }
    Serial.println("Camera init OK");
    return ESP_OK;
}

// Handle root page
void handle_root() {
    String html = "<html><body><h1>ESP32 Camera Stream</h1>";
    html += "<p>WiFi SSID: " + String(ssid) + "</p>";
    html += "<p>IP Address: " + WiFi.localIP().toString() + "</p>";
    html += "<img src=\"/video\" style=\"width:100%;\" />";
    html += "</body></html>";
    server.send(200, "text/html", html);
}

// MJPEG video stream handler
void handle_video_stream() {
    camera_fb_t * fb = NULL;
    char part_buf[64];

    // Set HTTP headers for multipart content
    server.setContentLength(CONTENT_LENGTH_UNKNOWN);
    server.send(200, "multipart/x-mixed-replace; boundary=frame");

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Camera capture failed");
            break;
        }

        // Send frame headers
        snprintf(part_buf, 64, "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
        server.sendContent(part_buf);
        server.sendContent((const char*)fb->buf, fb->len);
        server.sendContent("\r\n");

        esp_camera_fb_return(fb);

        // Ensure client is still connected
        if (!server.client().connected()) {
            break;
        }

        delay(33);  // Adjust delay for ~30fps (1000ms / 30fps ≈ 33ms)
    }
}

void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
    Serial.begin(115200);
    Serial.setDebugOutput(true);

    // Initialize camera
    if (init_camera() != ESP_OK) {
        Serial.println("Camera init failed");
        return;
    }

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Start web server
    server.on("/", handle_root);
    server.on("/video", handle_video_stream);  // Video stream route
    server.begin();
    Serial.println("HTTP server started");
}

void loop() {
    server.handleClient();
}
