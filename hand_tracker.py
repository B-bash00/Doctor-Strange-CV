import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence)
        
        self.landmarker = HandLandmarker.create_from_options(options)

    def process_frame(self, frame, timestamp_ms):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.landmarker.detect_for_video(mp_image, timestamp_ms)

    def is_palm_open(self, hand_landmarks):
        open_fingers = 0
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        for tip, pip in zip(tips, pips):
            if hand_landmarks[tip].y < hand_landmarks[pip].y:
                open_fingers += 1
                
        # Thumb simple check
        if hand_landmarks[4].x < hand_landmarks[3].x and hand_landmarks[4].y < hand_landmarks[3].y:
            open_fingers += 1
            
        return open_fingers >= 4

    def get_palm_center(self, hand_landmarks, width, height):
        x = int(hand_landmarks[9].x * width)
        y = int(hand_landmarks[9].y * height)
        return (x, y)

    def get_fingertips(self, hand_landmarks, width, height):
        tips = [8, 12, 16, 20]
        points = []
        for tip in tips:
            x = int(hand_landmarks[tip].x * width)
            y = int(hand_landmarks[tip].y * height)
            points.append((x, y))
        return points

    def get_hand_scale(self, hand_landmarks):
        # Distance between wrist(0) and middle MCP(9)
        dx = hand_landmarks[9].x - hand_landmarks[0].x
        dy = hand_landmarks[9].y - hand_landmarks[0].y
        dist = np.sqrt(dx**2 + dy**2)
        # Normalize to a usable scale factor roughly around 1.0 to 5.0
        return max(0.5, dist * 10)
