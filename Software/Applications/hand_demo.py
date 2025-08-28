#!/usr/bin/env python3
"""
hand_demo.py — lightweight hand detection demo

This script tries MediaPipe for hand landmarks if available. If MediaPipe
is not installed, it falls back to a simple skin-color contour detector.

Press 'q' to quit.
"""

import cv2
import time

try:
    import mediapipe as mp
    HAVE_MEDIAPIPE = True
except Exception:
    HAVE_MEDIAPIPE = False


def mediapipe_hand_demo():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                           min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("MediaPipe hand demo — press 'q' to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        annotated = frame.copy()
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(annotated, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('Hand Demo', annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def skin_color_fallback():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("Skin-color hand demo — press 'q' to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Simple skin color range; may need tuning for lighting/skin tones
        lower = (0, 30, 60)
        upper = (20, 150, 255)
        mask = cv2.inRange(hsv, lower, upper)
        # Morphology to clean mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        annotated = frame.copy()
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2000:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('Hand Demo (skin)', annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    if HAVE_MEDIAPIPE:
        try:
            mediapipe_hand_demo()
        except Exception as e:
            print('MediaPipe demo failed, falling back to skin-color method:', e)
            skin_color_fallback()
    else:
        print('MediaPipe not found — using skin-color fallback')
        skin_color_fallback()
