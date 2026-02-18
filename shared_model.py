import threading
import torch
from ultralytics import YOLO

print("🔵 Initializing Shared YOLO Model...")

device = 0 if torch.cuda.is_available() else "cpu"

if device == 0:
    print("✅ CUDA detected. Using GPU.")
else:
    print("⚠ CUDA not detected. Using CPU.")

model = YOLO("yolov8n.pt")
model.to(device)

print("🚀 YOLO model loaded successfully.")

model_lock = threading.Lock()
