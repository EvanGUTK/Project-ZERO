from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
picam2.configure(config)
picam2.set_controls({"AwbEnable": True, "ExposureTime": 0})  # Enable auto white balance and auto exposure
picam2.start()

cv2.namedWindow("CSI Camera Test", cv2.WINDOW_NORMAL)
print("Press 'q' to quit.")

while True:
    frame = picam2.capture_array()
    cv2.imshow("CSI Camera Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()