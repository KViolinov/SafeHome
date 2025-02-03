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




# import RPi.GPIO as GPIO
# import time

# PIR_PIN = 16  # GPIO pin connected to the PIR sensor output

# GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
# GPIO.setup(PIR_PIN, GPIO.IN)  # Set PIR pin as input

# print("PIR Sensor is ready...")

# try:
#     while True:
#         if GPIO.input(PIR_PIN):  # Motion detected
#             print("Motion detected!")
#             time.sleep(1)  # Wait to avoid multiple detections
#         else:
#             print("No motion")
#         time.sleep(0.5)

# except KeyboardInterrupt:
#     print("Exiting...")
#     GPIO.cleanup()  # Reset GPIO pins


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
















(.venv) konstantin@raspberrypi:~/Desktop $ /home/konstantin/Desktop/.venv/bin/python /home/konstantin/Desktop/test.py
/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/devices.py:300: PinFactoryFallback: Falling back from lgpio: No module named 'lgpio'
  warnings.warn(
Traceback (most recent call last):
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/pins/pi.py", line 411, in pin
    pin = self.pins[info]
          ~~~~~~~~~^^^^^^
KeyError: PinInfo(number=36, name='GPIO16', names=frozenset({16, 'GPIO16', 'J8:36', '16', 'BOARD36', 'WPI27', 'BCM16'}), pull='', row=18, col=2, interfaces=frozenset({'', 'uart', 'spi', 'dpi', 'gpio'}))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/konstantin/Desktop/test.py", line 31, in <module>
    motion_sensor = MotionSensor(PIR_PIN)
                    ^^^^^^^^^^^^^^^^^^^^^
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/devices.py", line 108, in __call__
    self = super().__call__(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/input_devices.py", line 588, in __init__
    super().__init__(
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/input_devices.py", line 257, in __init__
    super().__init__(
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/mixins.py", line 243, in __init__
    super().__init__(*args, **kwargs)
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/input_devices.py", line 79, in __init__
    super().__init__(pin, pin_factory=pin_factory)
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/devices.py", line 553, in __init__
    pin = self.pin_factory.pin(pin)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/pins/pi.py", line 413, in pin
    pin = self.pin_class(self, info)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/konstantin/Desktop/.venv/lib/python3.11/site-packages/gpiozero/pins/rpigpio.py", line 101, in __init__
    GPIO.setup(self._number, GPIO.IN, self.GPIO_PULL_UPS[self._pull])
RuntimeError: Cannot determine SOC peripheral base address
(.venv) konstantin@raspberrypi:~/Desktop $ 
