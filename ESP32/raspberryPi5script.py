# import cv2
# from flask import Flask, Response
# from pyngrok import ngrok
# import requests
# import subprocess
# import time
# import threading
# import serial

# # Serial Port Configuration (Update as needed)
# COM_PORT = "/dev/ttyUSB0"  # Change to your ESP32's serial port
# BAUD_RATE = 115200  # Ensure this matches ESP32's baud rate

# # Initialize serial connection
# try:
#     ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
#     print(f"Listening on {COM_PORT} at {BAUD_RATE} baud...")
# except serial.SerialException as e:
#     print(f"Error: {e}")
#     ser = None  # Prevent script crash if serial fails

# # Firebase Database URL
# FIREBASE_URL = "https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json"

# # Dictionary to store device links
# device_links = {}

# # Get device MAC address
# def get_mac_address():
#     try:
#         mac = subprocess.check_output("cat /sys/class/net/wlan0/address", shell=True).decode().strip()
#         return mac.replace(":", "-")
#     except Exception as e:
#         print(f"Error retrieving MAC address: {e}")
#         return "unknown-mac"

# device_mac = get_mac_address()

# # Initialize Flask app
# app = Flask(__name__)

# # Start Ngrok tunnel on port 5000
# try:
#     public_url = ngrok.connect(5000).public_url
#     print(f"Ngrok tunnel created: {public_url}")
# except Exception as e:
#     print(f"Error starting Ngrok: {e}")
#     public_url = "ngrok-error"

# # Store MAC and Ngrok link in dictionary with "/video_feed" appended
# if public_url != "ngrok-error":
#     device_links[device_mac] = f"{public_url}/video_feed"

# # Send device links to Firebase
# def send_device_links_to_firebase():
#     global device_links
#     try:
#         response = requests.get(FIREBASE_URL)
#         existing_data = response.json() if response.status_code == 200 else {}

#         for mac, url in device_links.items():
#             requests.patch(FIREBASE_URL, json={mac: url})

#         print("Device links successfully sent to Firebase.")
#     except Exception as e:
#         print(f"Error sending to Firebase: {e}")

# send_device_links_to_firebase()

# # Open USB webcam
# camera = cv2.VideoCapture(0)
# time.sleep(2)

# if not camera.isOpened():
#     print("Error: Could not access the webcam.")

# # Flag to control video streaming
# video_streaming = True

# # Function to generate video stream frames
# def generate_frames():
#     while True:
#         if not video_streaming:
#             time.sleep(0.1)  # Avoid busy-waiting
#             continue
#         success, frame = camera.read()
#         if not success:
#             break
#         ret, buffer = cv2.imencode('.jpg', frame)
#         if not ret:
#             continue
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# # Route for video stream
# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# # Route for index page
# @app.route('/')
# def index():
#     return f"Webcam Stream is running. <br> Access video at: <a href='{public_url}/video_feed'>{public_url}/video_feed</a>"

# # Function to capture an image
# def capture_image():
#     success, frame = camera.read()
#     if success:
#         filename = f"captured_{int(time.time())}.jpg"
#         cv2.imwrite(filename, frame)
#         print(f"Image saved: {filename}")
#     else:
#         print("Error capturing image.")

# # Function to listen for ESP32 messages
# def listen_to_esp():
#     global video_streaming
#     while True:
#         if ser and ser.in_waiting > 0:
#             message = ser.readline().decode("utf-8").strip()
#             print(f"ESP32 says: {message}")

#             if message.lower() == "yes":
#                 print("Stopping video stream and capturing image...")
#                 video_streaming = False
#                 capture_image()
#             elif message.lower() == "no":
#                 print("Resuming video stream...")
#                 video_streaming = True

# # Start serial listener in a separate thread
# serial_thread = threading.Thread(target=listen_to_esp, daemon=True)
# serial_thread.start()

# # Run the Flask app
# if __name__ == "__main__":
#     app.run(port=5000)





# from ultralytics import YOLO
# import cv2
# import os
# import firebase_admin
# from firebase_admin import credentials, storage, db
# import time
# import re
#
# # Firebase configuration
# cred = credentials.Certificate("/home/kviolinov/safehome-c4576-firebase-adminsdk-2rli7-6d7d62f21f.json")  # Ensure the correct path
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'safehome-c4576.appspot.com',
#     'databaseURL': 'https://safehome-c4576-default-rtdb.firebaseio.com'  # Add your database URL here
# })
#
# bucket = storage.bucket()
#
# def get_next_image():
#     blobs = bucket.list_blobs()
#     for blob in blobs:
#         # Only process images not already in checkedPhotos folder
#         if blob.name.endswith(".jpg") and not blob.name.startswith("checkedPhotos/"):
#             return blob.name
#     return None
#
# def download_image(blob_name, local_path):
#     blob = bucket.blob(blob_name)
#     blob.download_to_filename(local_path)
#     return local_path
#
# def run_yolo_detection(image_path):
#     try:
#         model = YOLO('yolov8n.pt')
#         frame = cv2.imread(image_path)
#         results = model.track(frame, persist=True)
#         return results
#     except Exception as e:
#         print(f"Error running YOLO detection: {e}")
#         return None
#
# def print_detection_results(file_name, results):
#     try:
#         boxes = results[0].boxes
#         class_names = results[0].names
#
#         detection_results = []
#         max_confidence = 0
#         detected_object = None
#
#         for box in boxes:
#             class_id = int(box.cls[0])
#             class_name = class_names[class_id]
#             confidence = box.conf[0]
#             detection_results.append({"class_name": class_name, "confidence": confidence})
#
#             # Update the max confidence and corresponding detected object
#             if confidence > max_confidence:
#                 max_confidence = confidence
#                 detected_object = class_name
#
#         # Print results to the terminal
#         print(f"Results for file: {file_name}")
#         for result in detection_results:
#             print(f"Detected {result['class_name']} with confidence {result['confidence']}")
#
#         # Return the detected object with the highest confidence
#         return detected_object
#     except Exception as e:
#         print(f"Error printing detection results: {e}")
#         return None
#
# def move_image_to_checked(blob_name):
#     try:
#         # Specify the new path in the 'checkedPhotos' folder
#         new_blob_name = f"checkedPhotos/{blob_name.split('/')[-1]}"
#         blob = bucket.blob(blob_name)
#         # Copy the image to 'checkedPhotos' folder
#         new_blob = bucket.blob(new_blob_name)
#         new_blob.rewrite(blob)
#         blob.delete()  # Delete the original image from the root folder
#
#         print(f"Moved image to 'checkedPhotos': {new_blob_name}")
#     except Exception as e:
#         print(f"Error moving image to 'checkedPhotos': {e}")
#
# def send_to_firebase(file_name, detected_object):
#     try:
#         # Replace invalid characters in the file name with underscores
#         sanitized_file_name = re.sub(r'[.$#[\]/]', '_', file_name)
#
#         ref = db.reference('/results/')
#         # Use the sanitized file_name as the key and detected_object as the value
#         ref.child(sanitized_file_name).set(detected_object)
#         print(f"Sent to Firebase: {sanitized_file_name} - {detected_object}")
#     except Exception as e:
#         print(f"Error sending data to Firebase: {e}")
#
# def main():
#     # Ensure the target directory exists for local storage
#     if not os.path.exists('model_data/pictures'):
#         os.makedirs('model_data/pictures')
#
#     while True:
#         image_file_name = get_next_image()
#         if image_file_name:
#             # Define the new local file path
#             local_image_path = 'model_data/pictures/temp.jpg'
#
#             # Download image from Firebase
#             local_image_path = download_image(image_file_name, local_image_path)
#             if local_image_path:
#                 # Run YOLO detection
#                 results = run_yolo_detection(local_image_path)
#                 if results:
#                     detected_object = print_detection_results(image_file_name, results)
#                     if detected_object:
#                         # Send detection result to Firebase
#                         send_to_firebase(image_file_name, detected_object)
#
#                     # Remove the local file after processing
#                     os.remove(local_image_path)
#
#                     # Move the image in Firebase to 'checkedPhotos'
#                     move_image_to_checked(image_file_name)
#                     print("Processed and moved the image to 'checkedPhotos'.")
#                 else:
#                     print("Error: YOLO detection failed.")
#             else:
#                 print("Error: Downloading image failed.")
#         else:
#             print("No images found. Checking again...")
#
#         # Sleep for a short duration to avoid constant polling
#         time.sleep(5)
#
# if __name__ == "__main__":
#     main()




# import spotipy
# import requests
# from PIL import Image
# from io import BytesIO
# import numpy as np
# import time
#
# from api_keys.api_keys import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
#
# client_id = SPOTIFY_CLIENT_ID
# client_secret = SPOTIFY_CLIENT_SECRET
#
# sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
#     client_id=client_id,
#     client_secret=client_secret,
#     redirect_uri='http://localhost:8888/callback',
#     scope="user-read-playback-state user-read-currently-playing"))  # Necessary permissions
#
#
# def get_current_song():
#     """Fetches the currently playing song and album cover URL."""
#     track = sp.current_playback()
#     if track and track.get('item'):
#         song_name = track['item']['name']
#         artist_name = track['item']['artists'][0]['name']
#         album_cover_url = track['item']['album']['images'][0]['url']  # Get the largest image
#         return song_name, artist_name, album_cover_url
#     return None, None, None
#
#
# def get_average_color(image_url):
#     """Downloads the image and calculates the average color."""
#     response = requests.get(image_url)
#     image = Image.open(BytesIO(response.content))
#     image = image.resize((50, 50))  # Reduce resolution for faster processing
#     np_image = np.array(image)
#
#     avg_color = np_image.mean(axis=(0, 1))  # Compute mean RGB values
#     return tuple(map(int, avg_color[:3]))  # Convert to integer RGB format
#
#
# def set_color(red, green, blue):
#     """Set the color using RGB values."""
#     url = "http://192.168.10.211/json/state"
#     data = {
#         "on": True,
#         "bri": 255,  # Optional: brightness
#         "seg": [{
#             "col": [[red, green, blue]]
#         }]
#     }
#     response = requests.post(url, json=data)
#     if response.status_code == 200:
#         print(f"✅ LED Color Set: RGB({red}, {green}, {blue})")
#     else:
#         print("⚠️ Failed to update LED color!")
#
#
# last_song = None
#
# while True:
#     song_name, artist_name, cover_url = get_current_song()
#
#     if song_name and song_name != last_song:  # Check if the song has changed
#         last_song = song_name
#         avg_color = get_average_color(cover_url)
#
#         print(f"🎵 Now Playing: {song_name} - {artist_name}")
#         print(f"🎨 Average Album Cover Color (RGB): {avg_color}")
#
#         # Set the LED color to match the album cover
#         set_color(*avg_color)
#
#     time.sleep(5)  # Wait for 5 seconds before checking again
#





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
FIREBASE_CREDENTIALS = "path/to/your-service-account.json"
FIREBASE_STORAGE_BUCKET = "safehome-c4576.appspot.com"

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
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {'storageBucket': FIREBASE_STORAGE_BUCKET})

    success, frame = camera.read()
    if success:
        # Generate filename with MAC address and timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{device_mac} - {timestamp}.jpg"
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

# Start serial listener in a separate thread
serial_thread = threading.Thread(target=listen_to_esp, daemon=True)
serial_thread.start()

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)
