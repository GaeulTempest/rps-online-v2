import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_gesture(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Detect hand gesture from frame
        Returns: (gesture_name, confidence)
        """
        if frame is None:
            return "none", 0.0
            
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand landmarks
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y])
                
                # Classify gesture based on finger positions
                gesture, confidence = self._classify_gesture(landmarks)
                return gesture, confidence
        
        return "none", 0.0
    
    def _classify_gesture(self, landmarks) -> Tuple[str, float]:
        """
        Classify gesture based on hand landmarks
        """
        if len(landmarks) < 21:
            return "none", 0.0
        
        # Get finger tip and pip landmarks
        # Thumb: 4, Index: 8, Middle: 12, Ring: 16, Pinky: 20
        # PIP joints: Thumb: 3, Index: 6, Middle: 10, Ring: 14, Pinky: 18
        
        thumb_tip = landmarks[4]
        thumb_pip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        
        # Count extended fingers
        fingers_up = []
        
        # Thumb (check if thumb tip is to the right of thumb pip for right hand)
        if thumb_tip[0] > thumb_pip[0]:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        # Other fingers (check if tip is above pip)
        finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
        finger_pips = [index_pip, middle_pip, ring_pip, pinky_pip]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if tip[1] < pip[1]:  # y coordinate decreases upward
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        # Classify based on finger pattern
        total_fingers = sum(fingers_up)
        confidence = 0.9  # Base confidence
        
        # Rock: All fingers down (fist)
        if fingers_up == [0, 0, 0, 0, 0]:
            return "rock", confidence
        
        # Paper: All fingers up (open hand)
        elif fingers_up == [1, 1, 1, 1, 1]:
            return "paper", confidence
        
        # Scissors: Index and middle finger up
        elif fingers_up == [0, 1, 1, 0, 0]:
            return "scissors", confidence
        
        # Additional patterns for better detection
        elif total_fingers == 0:
            return "rock", confidence * 0.8
        
        elif total_fingers >= 4:
            return "paper", confidence * 0.8
        
        elif total_fingers == 2 and fingers_up[1] == 1 and fingers_up[2] == 1:
            return "scissors", confidence * 0.8
        
        else:
            return "none", 0.5
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw hand landmarks on frame for debugging
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return frame