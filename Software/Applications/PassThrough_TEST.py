#!/usr/bin/env python3
"""
Simple CSI camera passthrough test for Pi 5.
Shows real-time camera feed in a window, similar to VR headset passthrough.
"""
from picamera2 import Picamera2
import cv2
import time

def main():
    # Initialize Picamera2
    picam2 = Picamera2()
    
    # Configure preview - BGR format for direct display with OpenCV
    config = picam2.create_preview_configuration(
        main={"size": (1920, 1080), "format": "BGR888"}  # Full HD for better screen capture
    )
    picam2.configure(config)
    
    # Start the camera
    picam2.start()
    
    # Create a named window and set it to fullscreen
    window_name = "CSI Passthrough Mirror"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    print("CSI Passthrough Mirror Test - Press 'q' to quit")
    print("Displaying mirrored camera feed...")
    
    try:
        while True:
            # Capture frame directly in BGR format (no conversion needed)
            frame = picam2.capture_array()
            
            # Display the frame fullscreen
            cv2.imshow(window_name, frame)
            
            # Break on 'q' press or ESC
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), 27]:  # 27 is ESC
                break
            
            # Small delay to control frame rate
            time.sleep(0.001)
    
    finally:
        # Clean up
        cv2.destroyAllWindows()
        picam2.stop()

if __name__ == "__main__":
    main()
