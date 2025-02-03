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
from gpiozero import MotionSensor  # Import gpiozero's MotionSensor class
import time
import threading
import firebase_admin
from firebase_admin import credentials, storage, db
import datetime
import uuid
import subprocess

# Initialize Firebase
cred = credentials.Certificate("safehome_sdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://safehome-c4576.appspot.com',
    'databaseURL': 'https://safehome-c4576-default-rtdb.firebaseio.com/'
})
bucket = storage.bucket()
ref = db.reference("/device_links")

# Get device MAC address
def get_mac_address():
    mac = subprocess.check_output("cat /sys/class/net/wlan0/address", shell=True).decode().strip()
    return mac.replace(":", "-")

device_mac = get_mac_address()

# PIR sensor setup using gpiozero
PIR_PIN = 16  # GPIO pin connected to the PIR sensor output
motion_sensor = MotionSensor(PIR_PIN)

# Initialize Flask app
app = Flask(__name__)

# Start Ngrok tunnel on port 5000
public_url = ngrok.connect(5000).public_url
print(f"Ngrok tunnel: {public_url}")
print(f"Access the video stream at: {public_url}/video_feed")

# Save Ngrok link to Firebase
db_entry = {device_mac: public_url}
ref.update(db_entry)
print("Ngrok link saved to Firebase.")

# Open USB webcam
camera = cv2.VideoCapture(0)  # Use 1 instead of 0 if you have multiple webcams

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
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

def capture_and_upload():
    success, frame = camera.read()
    if success:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"motion_{timestamp}.jpg"
        cv2.imwrite(image_path, frame)
        blob = bucket.blob(f"motion_images/{image_path}")
        blob.upload_from_filename(image_path)
        print(f"Image {image_path} uploaded to Firebase Storage.")

def pir_motion_detection():
    print("PIR Sensor is ready...")
    try:
        while True:
            motion_sensor.wait_for_motion()  # Wait for motion to be detected
            print("Motion detected!")
            capture_and_upload()
            time.sleep(1)  # Wait to avoid multiple detections
            motion_sensor.wait_for_no_motion()  # Wait for motion to stop
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting...")

# Run motion detection in a separate thread
motion_thread = threading.Thread(target=pir_motion_detection, daemon=True)
motion_thread.start()

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
