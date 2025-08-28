import cv2
import time
import os
import argparse

try:
    import mediapipe as mp
    HAVE_MEDIAPIPE = True
except Exception:
    HAVE_MEDIAPIPE = False

try:
    from picamera2 import Picamera2
    HAVE_PICAMERA2 = True
except Exception:
    HAVE_PICAMERA2 = False


def mediapipe_hand_demo():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                           min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    if HAVE_PICAMERA2:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
        picam2.configure(config)
        picam2.start()
        get_frame = lambda: (True, picam2.capture_array())
    else:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        get_frame = cap.read

    print("MediaPipe hand demo — press 'q' to quit")
    try:
        while True:
            ret, frame = get_frame()
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
    finally:
        if HAVE_PICAMERA2:
            picam2.stop()
        else:
            cap.release()
        cv2.destroyAllWindows()


def skin_color_fallback():
    if HAVE_PICAMERA2:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
        picam2.configure(config)
        picam2.start()
        get_frame = lambda: (True, picam2.capture_array())
    else:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        get_frame = cap.read

    print("Skin-color hand demo — press 'q' to quit")
    try:
        while True:
            ret, frame = get_frame()
            if not ret:
                break
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # Simple skin color range
            lower = (0, 30, 60)
            upper = (20, 150, 255)
            mask = cv2.inRange(hsv, lower, upper)
            # Clean mask
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
    finally:
        if HAVE_PICAMERA2:
            picam2.stop()
        else:
            cap.release()
        cv2.destroyAllWindows()


def save_frames_loop(capture_func, out_dir, max_frames=None, delay=0.03):
    os.makedirs(out_dir, exist_ok=True)
    if HAVE_PICAMERA2:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
        picam2.configure(config)
        picam2.start()
        get_frame = lambda: (True, picam2.capture_array())
    else:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        get_frame = cap.read

    count = 0
    print(f"Saving frames to {out_dir} — press Ctrl-C to stop")
    try:
        while True:
            ret, frame = get_frame()
            if not ret:
                break
            annotated = capture_func(frame)
            fname = os.path.join(out_dir, f"hand_{int(time.time()*1000)}_{count:04d}.jpg")
            cv2.imwrite(fname, annotated)
            count += 1
            if max_frames and count >= max_frames:
                break
            time.sleep(delay)
    finally:
        if HAVE_PICAMERA2:
            picam2.stop()
        else:
            cap.release()


def main():
    parser = argparse.ArgumentParser(description='Hand demo (MediaPipe or skin fallback)')
    parser.add_argument('--headless', action='store_true', help='Run headless and save annotated frames to disk')
    parser.add_argument('--outdir', default='/tmp/hand_demo_frames', help='Output directory for headless mode')
    parser.add_argument('--frames', type=int, default=20, help='Number of frames to save in headless mode')
    args = parser.parse_args()

    def mp_process(frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2,
                                         min_detection_confidence=0.5, min_tracking_confidence=0.5)
        results = hands.process(img)
        out = frame.copy()
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(out, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
        return out

    def skin_process(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = (0, 30, 60)
        upper = (20, 150, 255)
        mask = cv2.inRange(hsv, lower, upper)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        annotated = frame.copy()
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2000:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return annotated

    if args.headless:
        if HAVE_MEDIAPIPE:
            print('Running headless with MediaPipe...')
            save_frames_loop(mp_process, args.outdir, max_frames=args.frames)
        else:
            print('Running headless with skin-color fallback...')
            save_frames_loop(skin_process, args.outdir, max_frames=args.frames)
    else:
        if HAVE_MEDIAPIPE:
            try:
                mediapipe_hand_demo()
            except Exception as e:
                print('MediaPipe demo failed, falling back to skin-color method:', e)
                skin_color_fallback()
        else:
            print('MediaPipe not found — using skin-color fallback')
            skin_color_fallback()


if __name__ == '__main__':
    main()
