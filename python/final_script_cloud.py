from ultralytics import YOLO
import cv2
import os
import firebase_admin
from firebase_admin import credentials, storage, db
import time
import re

# Firebase configuration
cred = credentials.Certificate("/home/kviolinov/safehome-c4576-firebase-adminsdk-2rli7-6d7d62f21f.json")  # Ensure the correct path
firebase_admin.initialize_app(cred, {
    'storageBucket': 'safehome-c4576.appspot.com',
    'databaseURL': 'https://safehome-c4576-default-rtdb.firebaseio.com'  # Add your database URL here
})

bucket = storage.bucket()

def get_next_image():
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name.endswith(".jpg"):
            return blob.name
    return None

def download_image(blob_name, local_path):
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_path)
    return local_path

def run_yolo_detection(image_path):
    try:
        model = YOLO('yolov8n.pt')
        frame = cv2.imread(image_path)
        results = model.track(frame, persist=True)
        return results
    except Exception as e:
        print(f"Error running YOLO detection: {e}")
        return None

def print_detection_results(file_name, results):
    try:
        boxes = results[0].boxes
        class_names = results[0].names

        detection_results = []
        max_confidence = 0
        detected_object = None

        for box in boxes:
            class_id = int(box.cls[0])
            class_name = class_names[class_id]
            confidence = box.conf[0]
            detection_results.append({"class_name": class_name, "confidence": confidence})

            # Update the max confidence and corresponding detected object
            if confidence > max_confidence:
                max_confidence = confidence
                detected_object = class_name

        # Print results to the terminal
        print(f"Results for file: {file_name}")
        for result in detection_results:
            print(f"Detected {result['class_name']} with confidence {result['confidence']}")

        # Print the detected object with the highest confidence
        if detected_object:
            print(f"Detected object with highest confidence: {detected_object} ({max_confidence})")

        return detected_object
    except Exception as e:
        print(f"Error printing detection results: {e}")
        return None

def delete_image(blob_name):
    blob = bucket.blob(blob_name)
    blob.delete()


def send_to_firebase(file_name, detected_object):
    try:
        # Replace invalid characters in the file name with underscores
        sanitized_file_name = re.sub(r'[.$#[\]/]', '_', file_name)

        ref = db.reference('/results/')
        # Use the sanitized file_name as the key and detected_object as the value
        ref.child(sanitized_file_name).set(detected_object)
        print(f"Sent to Firebase: {sanitized_file_name} - {detected_object}")
    except Exception as e:
        print(f"Error sending data to Firebase: {e}")


def main():
    # Ensure the target directory exists
    if not os.path.exists('model_data/pictures'):
        os.makedirs('model_data/pictures')

    while True:
        image_file_name = get_next_image()
        if image_file_name:
            # Define the new local file path
            local_image_path = 'model_data/pictures/temp.jpg'

            local_image_path = download_image(image_file_name, local_image_path)
            if local_image_path:
                results = run_yolo_detection(local_image_path)
                if results:
                    detected_object = print_detection_results(image_file_name, results)
                    if detected_object:
                        send_to_firebase(image_file_name, detected_object)
                    os.remove(local_image_path)
                    delete_image(image_file_name)
                    print("Processed and cleaned up the image.")
                else:
                    print("Error: YOLO detection failed.")
            else:
                print("Error: Downloading image failed.")
        else:
            print("No images found. Checking again...")

        # Sleep for a short duration to avoid constant polling
        time.sleep(5)

if __name__ == "__main__":
    main()
