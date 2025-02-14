import cv2
from flask import Flask, Response
from pyngrok import ngrok
import requests
import subprocess
import time
import threading
import serial

# Serial Port Configuration (Update as needed)
COM_PORT = "COM3"  # Change to your ESP32's serial port
BAUD_RATE = 115200  # Ensure this matches ESP32's baud rate

# Initialize serial connection
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Listening on {COM_PORT} at {BAUD_RATE} baud...")
except serial.SerialException as e:
    print(f"Error: {e}")
    ser = None  # Prevent script crash if serial fails

# Firebase Database URL
FIREBASE_URL = "https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json"

# Dictionary to store device links
device_links = {}

# Get device MAC address
def get_mac_address():
    try:
        mac = subprocess.check_output("cat /sys/class/net/wlan0/address", shell=True).decode().strip()
        return mac.replace(":", "-")
    except Exception as e:
        print(f"Error retrieving MAC address: {e}")
        return "unknown-mac"

device_mac = get_mac_address()

# Initialize Flask app
app = Flask(__name__)

# Start Ngrok tunnel on port 5000
try:
    public_url = ngrok.connect(5000).public_url
    print(f"Ngrok tunnel created: {public_url}")
except Exception as e:
    print(f"Error starting Ngrok: {e}")
    public_url = "ngrok-error"

# Store MAC and Ngrok link in dictionary with "/video_feed" appended
if public_url != "ngrok-error":
    device_links[device_mac] = f"{public_url}/video_feed"

# Send device links to Firebase
def send_device_links_to_firebase():
    global device_links
    try:
        response = requests.get(FIREBASE_URL)
        existing_data = response.json() if response.status_code == 200 else {}

        for mac, url in device_links.items():
            requests.patch(FIREBASE_URL, json={mac: url})

        print("Device links successfully sent to Firebase.")
    except Exception as e:
        print(f"Error sending to Firebase: {e}")

send_device_links_to_firebase()

# Open USB webcam
camera = cv2.VideoCapture(0)
time.sleep(2)

if not camera.isOpened():
    print("Error: Could not access the webcam.")

# Flag to control video streaming
video_streaming = True

# Function to generate video stream frames
def generate_frames():
    while True:
        if not video_streaming:
            time.sleep(0.1)  # Avoid busy-waiting
            continue
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for index page
@app.route('/')
def index():
    return f"Webcam Stream is running. <br> Access video at: <a href='{public_url}/video_feed'>{public_url}/video_feed</a>"

# Function to capture an image
def capture_image():
    success, frame = camera.read()
    if success:
        filename = f"captured_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Image saved: {filename}")
    else:
        print("Error capturing image.")

# Function to listen for ESP32 messages
def listen_to_esp():
    global video_streaming
    while True:
        if ser and ser.in_waiting > 0:
            message = ser.readline().decode("utf-8").strip()
            print(f"ESP32 says: {message}")

            if message.lower() == "yes":
                print("Stopping video stream and capturing image...")
                video_streaming = False
                capture_image()
            elif message.lower() == "no":
                print("Resuming video stream...")
                video_streaming = True

# Start serial listener in a separate thread
serial_thread = threading.Thread(target=listen_to_esp, daemon=True)
serial_thread.start()

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)






import serial

# Change this to your ESP32's port
COM_PORT = "COM3"  # Example for Windows, change to "/dev/ttyUSB0" for Linux/macOS
BAUD_RATE = 115200  # Match this with your ESP32's baud rate

try:
    # Open the serial port
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Listening on {COM_PORT} at {BAUD_RATE} baud...")

    while True:
        if ser.in_waiting > 0:
            # Read a line from the serial port
            message = ser.readline().decode("utf-8").strip()
            print(f"ESP32 says: {message}")

except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("User interrupted. Closing serial port...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
