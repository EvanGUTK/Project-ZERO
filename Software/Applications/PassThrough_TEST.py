#!/usr/bin/env python3
"""
AR-style desktop overlay on CSI camera feed.
Simulates AR glasses view by blending desktop capture with camera feed.
"""
from picamera2 import Picamera2
import cv2
import numpy as np
import time
from PIL import Image
import subprocess
import threading

class AROverlay:
    def __init__(self):
        # Initialize camera
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (1920, 1080), "format": "BGR888"}
        )
        self.picam2.configure(config)
        
        # Initialize screen capture (using scrot)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'scrot'], check=True)
        
        # Create windows
        self.main_window = "AR View"
        self.controls_window = "Controls"
        cv2.namedWindow(self.main_window, cv2.WINDOW_NORMAL)
        cv2.namedWindow(self.controls_window, cv2.WINDOW_NORMAL)
        
        # Initialize controls
        self.exposure = 0
        self.brightness = 1.0
        self.contrast = 1.0
        self.overlay_opacity = 0.5
        self.window_x = 0
        self.window_y = 0
        self.show_original = True
        self.fps_list = []
        self.last_time = time.time()
        
        # Create trackbars
        cv2.createTrackbar('Exposure', self.controls_window, 0, 100, self.on_exposure)
        cv2.createTrackbar('Brightness', self.controls_window, 50, 100, self.on_brightness)
        cv2.createTrackbar('Contrast', self.controls_window, 50, 100, self.on_contrast)
        cv2.createTrackbar('Overlay Opacity', self.controls_window, 50, 100, self.on_opacity)
        cv2.createTrackbar('Window X', self.controls_window, 0, 1920, self.on_window_x)
        cv2.createTrackbar('Window Y', self.controls_window, 0, 1080, self.on_window_y)
        
    def on_exposure(self, val):
        self.exposure = val - 50
        
    def on_brightness(self, val):
        self.brightness = val / 50.0
        
    def on_contrast(self, val):
        self.contrast = val / 50.0
        
    def on_opacity(self, val):
        self.overlay_opacity = val / 100.0
        
    def on_window_x(self, val):
        self.window_x = val
        
    def on_window_y(self, val):
        self.window_y = val
        
    def calculate_fps(self):
        current_time = time.time()
        self.fps_list.append(1 / (current_time - self.last_time))
        self.last_time = current_time
        if len(self.fps_list) > 30:
            self.fps_list.pop(0)
        return sum(self.fps_list) / len(self.fps_list)
        
    def adjust_image(self, frame):
        # Apply brightness and contrast
        adjusted = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=self.brightness * 50)
        return adjusted
        
    def run(self):
        self.picam2.start()
        
        try:
            while True:
                # Capture camera frame
                camera_frame = self.picam2.capture_array()
                
                # Capture screen using scrot
                subprocess.run(['scrot', '/tmp/screen.png'], check=True)
                screen = Image.open('/tmp/screen.png')
                screen_frame = np.array(screen)
                screen_frame = cv2.cvtColor(screen_frame, cv2.COLOR_RGB2BGR)
                
                # Resize screen frame to match camera frame
                screen_frame = cv2.resize(screen_frame, (camera_frame.shape[1], camera_frame.shape[0]))
                
                # Apply image adjustments
                camera_frame = self.adjust_image(camera_frame)
                
                # Blend frames
                blended = cv2.addWeighted(camera_frame, 1-self.overlay_opacity, 
                                        screen_frame, self.overlay_opacity, 0)
                
                # Calculate FPS
                fps = self.calculate_fps()
                
                # Add FPS counter
                cv2.putText(blended, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show side by side if enabled
                if self.show_original:
                    display = np.hstack((camera_frame, blended))
                else:
                    display = blended
                
                # Display the result
                cv2.moveWindow(self.main_window, self.window_x, self.window_y)
                cv2.imshow(self.main_window, display)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # ESC
                    break
                elif key == ord('s'):  # Toggle side-by-side view
                    self.show_original = not self.show_original
                
        finally:
            cv2.destroyAllWindows()
            self.picam2.stop()
            subprocess.run(['rm', '-f', '/tmp/screen.png'], check=False)

def main():
    ar = AROverlay()
    print("AR Desktop Overlay Test")
    print("Controls:")
    print("  - 'q' or ESC to quit")
    print("  - 's' to toggle side-by-side view")
    print("  - Use sliders to adjust settings")
    ar.run()

if __name__ == "__main__":
    main()
