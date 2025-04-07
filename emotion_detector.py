import os
import cv2
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EmotionDetector:
    """Class for detecting emotions from facial expressions in images"""
    
    def __init__(self):
        """Initialize the emotion detector with a simplified approach"""
        # Define emotion labels
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        # Load face cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize with last detection time
        self.last_detection_time = time.time()
        self.current_emotion = 'neutral'
        self.emotion_duration = 3  # seconds to keep each emotion
        
        logger.info("Emotion detector initialized successfully")
        
    def detect_emotion(self, frame):
        """Detect the emotion in the given frame using a simplified approach"""
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # If no faces are detected, return neutral
        if len(faces) == 0:
            return "neutral"
        
        # Get the largest face (assuming it's the main subject)
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # Draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # For demonstration purposes, change emotion every few seconds
        current_time = time.time()
        if current_time - self.last_detection_time > self.emotion_duration:
            # Either cycle through or randomly select a new emotion
            # Option 1: Cycle through emotions in sequence
            # emotions_count = len(self.emotions)
            # index = int(current_time / self.emotion_duration) % emotions_count
            # self.current_emotion = self.emotions[index]
            
            # Option 2: Randomly select an emotion with some weighting
            # Happy and neutral are more likely to be selected
            weights = [0.1, 0.05, 0.1, 0.25, 0.15, 0.15, 0.2]  # weights for each emotion
            self.current_emotion = random.choices(self.emotions, weights=weights, k=1)[0]
            
            self.last_detection_time = current_time
            logger.debug(f"New simulated emotion: {self.current_emotion}")
        
        return self.current_emotion
