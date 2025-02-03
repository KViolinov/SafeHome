# import cv2
# from flask import Flask, Response
# from pyngrok import ngrok

# # Initialize Flask app
# app = Flask(__name__)

# # Start Ngrok tunnel on port 5000
# public_url = ngrok.connect(5000).public_url
# print(f"Ngrok tunnel: {public_url}")
# print(f"Access the video stream at: {public_url}/video_feed")

# # Open USB webcam
# camera = cv2.VideoCapture(2)  # Use 1 instead of 0 if you have multiple webcams

# def generate_frames():
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/')
# def index():
#     return f"Webcam Stream is running. <br> Access video at: <a href='{public_url}/video_feed'>{public_url}/video_feed</a>"

# if __name__ == "__main__":
#     app.run(port=5000)






import cv2
from flask import Flask, Response
from pyngrok import ngrok
import firebase_admin
from firebase_admin import credentials, storage, db
import subprocess
import time

# Initialize Firebase
cred = credentials.Certificate("safehome_sdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://safehome-c4576.appspot.com',
    'databaseURL': 'https://safehome-c4576-default-rtdb.firebaseio.com/'
})
ref = db.reference("/device_links")

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

# Save Ngrok link to Firebase
if public_url != "ngrok-error":
    ref.update({device_mac: public_url})
    print(f"Ngrok link saved to Firebase: {device_mac} -> {public_url}")

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
import atexit
@atexit.register
def cleanup():
    if camera.isOpened():
        camera.release()
        print("Camera released.")

if __name__ == "__main__":
    app.run(port=5000)

















from gpiozero import MotionSensor
from signal import pause

pir = MotionSensor(18)

def motion_function():
    print("Motion Detected")

def no_motion_function():
    print("Motion stopped")

pir.when_motion = motion_function
pir.when_no_motion = no_motion_function

pause()
