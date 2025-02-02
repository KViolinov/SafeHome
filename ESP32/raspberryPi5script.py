import cv2
from flask import Flask, Response
from pyngrok import ngrok

# Initialize Flask app
app = Flask(__name__)

# Start Ngrok tunnel on port 5000
public_url = ngrok.connect(5000).public_url
print(f"Ngrok tunnel: {public_url}")
print(f"Access the video stream at: {public_url}/video_feed")

# Open USB webcam
camera = cv2.VideoCapture(2)  # Use 1 instead of 0 if you have multiple webcams

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

if __name__ == "__main__":
    app.run(port=5000)
