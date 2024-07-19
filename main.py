# working version for images/pictures

from ultralytics import YOLO
import cv2
import os

def print_detection_results(results):
    # Extract the detection information
    boxes = results[0].boxes
    class_names = results[0].names

    for box in boxes:
        class_id = int(box.cls[0])
        class_name = class_names[class_id]
        confidence = box.conf[0]
        print(f"Detected: {class_name} with confidence: {confidence:.2f}")

# Ensure to provide a valid path to your image file
imagePath = 'model_data/pictures/presi.jpg'

# Check if the file exists at the specified path
if not os.path.isfile(imagePath):
    print(f"Error: The file {imagePath} does not exist.")
    exit()

# Load the image
frame = cv2.imread(imagePath)

# Check if the image was loaded successfully
if frame is None:
    print("Error: Could not read image.")
    exit()

# Load the YOLO model
try:
    model = YOLO('yolov8n.pt')
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"Error: Could not load YOLO model. {e}")
    exit()

# Run the detection on the image
try:
    results = model.track(frame, persist=True)
    print("Detection results obtained successfully.")
except Exception as e:
    print(f"Error during detection: {e}")
    exit()

# Print the detection results to the terminal
print_detection_results(results)

# Plot the results on the image
try:
    frame_ = results[0].plot()
    print("Results plotted on image successfully.")
except Exception as e:
    print(f"Error while plotting results: {e}")
    exit()

# Display the image with the results
cv2.imshow('image', frame_)

# Wait until a key is pressed
cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()



# working version for video


# from ultralytics import YOLO
# import cv2
#
# # Ensure to provide a valid path to your video file
# videoPath = 'model_data/videos/video.mp4'
# cap = cv2.VideoCapture(videoPath)
#
# # Check if the video path is valid
# if not cap.isOpened():
#     print("Error: Could not open video.")
#     exit()
#
# # Load the YOLO model
# model = YOLO('yolov8n.pt')
#
# while True:
#     ret, frame = cap.read()
#
#     # If frame reading was not successful, break the loop
#     if not ret:
#         print("Error: Could not read frame.")
#         break
#
#     # Run the tracking on the current frame
#     results = model.track(frame, persist=True)
#
#     # Plot the results on the frame
#     frame_ = results[0].plot()
#
#     # Display the frame
#     cv2.imshow('frame', frame_)
#
#     # Break the loop if 'q' key is pressed
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         break
#
# # Release the video capture and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()
