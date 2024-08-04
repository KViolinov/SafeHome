from ultralytics import YOLO
import cv2
import os
import pyrebase
import time

# Firebase configuration
config = { }

# Connecting to Firebase
try:
    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    database = firebase.database()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit()


def get_last_unprocessed_image():  # Function to check the last unprocessed image
    try:
        all_files = storage.list_files()
        for file in all_files:
            if file.name.endswith(".jpg"):
                # Fetch metadata or a way to check the flag (implement as needed)
                metadata = database.child("images").child(file.name.replace("/", "_")).get().val()
                if metadata and not metadata.get('flag', False):
                    return file.name
    except Exception as e:
        print(f"Error retrieving unprocessed image: {e}")
    return None


def download_image(file_name, local_path):  # Function to download the picture from Firebase to local PC
    try:
        storage.child(file_name).download(local_path)
        return local_path
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def run_yolo_detection(image_path):  # Function to run the YOLOv8 model
    try:
        model = YOLO('yolov8n.pt')
        frame = cv2.imread(image_path)
        results = model.track(frame, persist=True)
        return results
    except Exception as e:
        print(f"Error running YOLO detection: {e}")
        return None


def print_detection_results(results):  # Function to print the result from the YOLOv8 model
    try:
        boxes = results[0].boxes
        class_names = results[0].names

        detection_results = []
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = class_names[class_id]
            confidence = box.conf[0]
            detection_results.append({"class_name": class_name, "confidence": confidence})
        return detection_results
    except Exception as e:
        print(f"Error printing detection results: {e}")
        return []


def upload_detection_results(file_name, results):  # Function to upload/update the results Firebase
    try:
        database.child("detection_results").child(file_name.replace("/", "_")).set(results)
        database.child("images").child(file_name.replace("/", "_")).update({"flag": True})
    except Exception as e:
        print(f"Error uploading detection results: {e}")


def main():
    while True:
        image_file_name = get_last_unprocessed_image()
        if image_file_name:
            local_image_path = download_image(image_file_name, 'images/temp.jpg')
            if local_image_path:
                results = run_yolo_detection(local_image_path)
                if results:
                    detection_results = print_detection_results(results)
                    upload_detection_results(image_file_name, detection_results)
                    os.remove(local_image_path)
                    print("Processed and cleaned up the image.")
                else:
                    print("Error: YOLO detection failed.")
            else:
                print("Error: Downloading image failed.")
        else:
            print("No unprocessed images found. Checking again...")

        # Check if 'q' is pressed to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exit requested by user.")
            break

        # Sleep for a short duration to avoid constant polling
        time.sleep(5)


if __name__ == "__main__":
    main()
