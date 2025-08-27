#!/usr/bin/env python3
# CAMTEST.py — ultra-simple YOLOv8n + CSI cam test on Pi5

import cv2, time
from picamera2 import Picamera2
from ultralytics import YOLO

# Load YOLOv8 nano model
model = YOLO("yolov8n.pt")

# Start Pi camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
picam2.configure(config)
picam2.start()

# OpenCV preview window
cv2.namedWindow("CAMTEST", cv2.WINDOW_NORMAL)

print("[INFO] Starting camera test... press 'q' to quit")
t0, frames = time.time(), 0

try:
    while True:
        frame = picam2.capture_array()

        # Run YOLO inference
        results = model(frame, verbose=False)
        annotated = results[0].plot()

        # Show FPS every second
        frames += 1
        if time.time() - t0 >= 1.0:
            print(f"FPS: {frames}")
            t0, frames = time.time(), 0

        # Show window
        cv2.imshow("CAMTEST", annotated)
        if (cv2.waitKey(1) & 0xFF) in (27, ord("q")):  # ESC or q to quit
            break

except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
    cv2.destroyAllWindows()