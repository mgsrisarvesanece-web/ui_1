import csv
import os
import time

class Logger:

    def __init__(self, filename="system_logs.csv"):
        self.filename = filename
        self.last_write_time = 0

    def log(self, camera_id, sri_left, sri_right, status_left, status_right):
        now = time.time()

        if now - self.last_write_time < 1:
            return

        file_exists = os.path.isfile(self.filename)

        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    "Timestamp",
                    "Camera",
                    "Left_SRI",
                    "Right_SRI",
                    "Left_Status",
                    "Right_Status"
                ])

            writer.writerow([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                camera_id,
                sri_left,
                sri_right,
                status_left,
                status_right
            ])

        self.last_write_time = now
