import cv2
from flask import Flask, Response  # Flask serves the video as a web page

CAMERA_INDEX = 0  # 0 = first camera; try 1 or 2 if it's the wrong one

# Rotation that makes the image upright; set to None for no rotation
ROTATION = cv2.ROTATE_90_COUNTERCLOCKWISE

app = Flask(__name__)
cap = cv2.VideoCapture(CAMERA_INDEX)  # open the camera once at startup
if not cap.isOpened():
    raise SystemExit("Could not open camera")

def frames():
    """Yield camera frames as a JPEG stream (MJPEG)."""
    while True:
        ok, frame = cap.read()  # grab one frame
        if not ok:
            break
        if ROTATION is not None:
            frame = cv2.rotate(frame, ROTATION)  # same rotation as before
        # Encode as JPEG so a browser can display it
        _, jpg = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
               + jpg.tobytes() + b"\r\n")

@app.route("/")
def index():
    return Response(frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# 0.0.0.0 lets other devices on your WiFi connect
app.run(host="0.0.0.0", port=5000)