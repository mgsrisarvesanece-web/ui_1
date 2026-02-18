import cv2
import threading
import time
import numpy as np
from ultralytics import YOLO

# Shared storage
camera_frames = {}
camera_sri = {}

class CameraWorker(threading.Thread):

    def __init__(self, camera_id, source):
        super().__init__()
        self.camera_id = camera_id
        self.source = source
        self.daemon = True

    def run(self):

        print(f"🚀 Starting {self.camera_id}")
        cap = cv2.VideoCapture(self.source)

        if not cap.isOpened():
            print(f"❌ {self.camera_id} failed to open")
            return

        model = YOLO("yolov8n.pt")

        while True:

            ret, frame = cap.read()
            if not ret:
                continue

            height, width, _ = frame.shape
            mid_x = width // 2

            # Detection
            results = model.predict(frame, imgsz=640, conf=0.35, verbose=False)
            boxes = results[0].boxes

            left_count = 0
            right_count = 0

            if boxes is not None:
                for b in boxes:
                    if int(b.cls[0]) != 0:
                        continue

                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    cx = (x1 + x2) // 2

                    if cx < mid_x:
                        left_count += 1
                        color = (0, 255, 0)
                    else:
                        right_count += 1
                        color = (0, 0, 255)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Simple SRI Calculation
            total_people = left_count + right_count
            sri_value = min(total_people / 20.0, 1.0)  # normalize

            camera_sri[self.camera_id] = sri_value

            # Draw SRI
            cv2.putText(frame,
                        f"SRI: {round(sri_value,2)}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255) if sri_value > 0.75 else (0,255,0),
                        3)

            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            camera_frames[self.camera_id] = buffer.tobytes()

            time.sleep(0.03)
