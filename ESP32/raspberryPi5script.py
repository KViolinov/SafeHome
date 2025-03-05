import cv2
from flask import Flask, Response
from pyngrok import ngrok
import requests
import subprocess
import time
import threading
import serial
import requests
import time
import firebase_admin
from firebase_admin import credentials, storage
import os
from datetime import datetime


# Serial Port Configuration (Update as needed)
COM_PORT = "/dev/ttyUSB0"  # Change to your ESP32's serial port
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

# Initialize Firebase Admin SDK (Update with your service account JSON file path)
FIREBASE_CREDENTIALS = "/home/konstantin/Desktop/safehome-c4576-firebase-adminsdk-2rli7-627a495f20.json"
FIREBASE_STORAGE_BUCKET = "safehome-c4576.appspot.com"

# Dictionary to store device links
device_links = {}

# Get device MAC address
def get_mac_address():
    try:
        mac = subprocess.check_output("cat /sys/class/net/wlan0/address", shell=True).decode().strip()
        return mac.replace("-", ":")
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

# Function to capture an image with a new filename format
def capture_image():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {'storageBucket': FIREBASE_STORAGE_BUCKET})

    success, frame = camera.read()
    if success:
        # Generate filename with MAC address and a custom timestamp format
        timestamp = datetime.now().strftime("%d_%m_%H_%M_%S")  # Use day_month_hour_minute_second format
        filename = f"{device_mac}_{timestamp}.jpg"  # Updated filename format
        filepath = os.path.join("/tmp", filename)  # Temporary directory to store image

        # Save image locally
        cv2.imwrite(filepath, frame)
        print(f"Image saved: {filepath}")

        # Upload image to Firebase Storage
        try:
            bucket = storage.bucket()
            blob = bucket.blob(f"{filename}")  # Store in 'captured_images' folder
            blob.upload_from_filename(filepath)
            blob.make_public()  # Make it accessible (optional)
            print(f"Image uploaded to Firebase: {blob.public_url}")
        except Exception as e:
            print(f"Error uploading to Firebase: {e}")

        # Delete the local file after upload
        try:
            os.remove(filepath)
            print(f"Deleted local image: {filepath}")
        except Exception as e:
            print(f"Error deleting local image: {e}")

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
