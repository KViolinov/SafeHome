import cv2
from flask import Flask, Response
from pyngrok import ngrok
import requests
import subprocess
import time
import atexit

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

# Store MAC and Ngrok link in dictionary
if public_url != "ngrok-error":
    device_links[device_mac] = public_url

# Send device links to Firebase
def send_device_links_to_firebase():
    global device_links

    try:
        print("Checking existing device links in Firebase...")

        # Fetch existing links from Firebase
        response = requests.get(FIREBASE_URL)
        existing_data = response.json() if response.status_code == 200 else {}

        if not existing_data:
            print("No existing data found. Adding new links to Firebase.")

        # Update existing entries or add new ones
        for mac, url in device_links.items():
            if existing_data and mac in existing_data:
                print(f"Updating link for MAC: {mac} in Firebase.")
            else:
                print(f"Adding new link for MAC: {mac} in Firebase.")

            # Update Firebase with the new or updated link
            requests.patch(FIREBASE_URL, json={mac: url})

        print("Device links successfully sent to Firebase.")

    except Exception as e:
        print(f"Error sending to Firebase: {e}")

# Send device link to Firebase
send_device_links_to_firebase()

# Open USB webcam (wait for availability)
camera = cv2.VideoCapture(0)
time.sleep(2)  # Give some time for the camera to initialize

if not camera.isOpened():
    print("Error: Could not access the webcam.")

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("Error: Failed to read frame from camera.")
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return f"Webcam Stream is running. <br> Access video at: <a href='{public_url}/video_feed'>{public_url}/video_feed</a>"

# Gracefully close camera on exit
@atexit.register
def cleanup():
    if camera.isOpened():
        camera.release()
        print("Camera released.")

if __name__ == "__main__":
    app.run(port=5000)





# from gpiozero import MotionSensor
# from signal import pause
# import cv2
# import time

# pir = MotionSensor(20)

# def motion_function():
#     print("Motion Detected")
#     # Open the webcam (0 is usually the default camera)
#     cap = cv2.VideoCapture(0)
    
#     if not cap.isOpened():
#         print("Error: Could not access the webcam")
#         return
    
#     # Capture a single frame
#     ret, frame = cap.read()
    
#     if ret:
#         # Save the captured image with a timestamp
#         filename = f"motion_{int(time.time())}.jpg"
#         cv2.imwrite(filename, frame)
#         print(f"Picture taken and saved as {filename}")
    
#     # Release the webcam
#     cap.release()

# def no_motion_function():
#     print("Motion stopped")

# pir.when_motion = motion_function
# pir.when_no_motion = no_motion_function

# pause()
