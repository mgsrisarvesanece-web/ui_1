import cv2

for i in range(6):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera index {i} is working")
        cap.release()
    else:
        print(f"Camera index {i} NOT working")
