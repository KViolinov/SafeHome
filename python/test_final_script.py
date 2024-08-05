from ultralytics import YOLO
import cv2
import os
import firebase_admin
from firebase_admin import credentials, storage
import time

# Firebase configuration
cred = credentials.Certificate("model_data/firebase/safehome-c4576-firebase-adminsdk-2rli7-6d7d62f21f.json")  # Ensure the correct path
firebase_admin.initialize_app(cred, {
    'storageBucket': 'safehome-c4576.appspot.com'
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
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = class_names[class_id]
            confidence = box.conf[0]
            detection_results.append({"class_name": class_name, "confidence": confidence})

        # Print results to the terminal
        print(f"Results for file: {file_name}")
        for result in detection_results:
            print(f"Detected {result['class_name']} with confidence {result['confidence']}")

        return detection_results
    except Exception as e:
        print(f"Error printing detection results: {e}")
        return []



def delete_image(blob_name):
    blob = bucket.blob(blob_name)
    blob.delete()


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
                    print_detection_results(image_file_name, results)  # Pass file name here
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
