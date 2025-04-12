import logging
import time
import random
import numpy as np
import base64
import os

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available. Face detection will be simulated.")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EmotionDetector:
    """Class for detecting emotions from facial expressions in images"""
    
    def __init__(self):
        """Initialize the emotion detector with a simplified approach"""
        # Define emotion labels
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        # Initialize with last detection time
        self.last_detection_time = time.time()
        self.current_emotion = 'neutral'
        self.emotion_duration = 7  # seconds to keep each emotion (increased for better UX)
        self.manual_mode = False   # Track if emotion was manually set
        self.manual_emotion = None # Store manually selected emotion
        
        # Load face detection model if OpenCV is available
        self.face_cascade = None
        if OPENCV_AVAILABLE:
            try:
                # Try to load the face cascade from OpenCV's included data
                opencv_dir = os.path.dirname(cv2.__file__)
                haar_file = os.path.join(opencv_dir, 'data', 'haarcascade_frontalface_default.xml')
                
                if os.path.exists(haar_file):
                    self.face_cascade = cv2.CascadeClassifier(haar_file)
                    logger.info(f"Loaded face cascade from {haar_file}")
                else:
                    # Fall back to the direct path method
                    self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    logger.info("Loaded face cascade from cv2.data.haarcascades")
            except Exception as e:
                logger.error(f"Error loading face cascade: {e}")
                self.face_cascade = None
        
        logger.info("Emotion detector initialized successfully")
    
    def set_manual_emotion(self, emotion):
        """Manually set the emotion"""
        if emotion in self.emotions:
            self.manual_emotion = emotion
            self.manual_mode = True
            logger.info(f"Emotion manually set to: {emotion}")
            return emotion
        else:
            logger.warning(f"Invalid emotion: {emotion}. Must be one of {self.emotions}")
            return self.current_emotion
    
    def detect_emotion(self, frame=None):
        """
        Detect the emotion automatically or return the manually set emotion
        
        In auto mode: Uses weighted random selection to simulate emotion detection
        In manual mode: Returns the manually selected emotion
        With frame data: Attempts real face detection if OpenCV is available
        """
        # If manual emotion was set, return that
        if self.manual_mode and self.manual_emotion:
            # Reset manual mode after a period to allow auto-detection to resume
            current_time = time.time()
            if current_time - self.last_detection_time > self.emotion_duration * 2:
                logger.debug("Resetting from manual to auto mode")
                self.manual_mode = False
            else:
                return self.manual_emotion
        
        # If we have frame data and OpenCV, try to detect faces
        if frame and OPENCV_AVAILABLE and self.face_cascade:
            try:
                # Convert base64 frame to numpy array for OpenCV
                if isinstance(frame, str) and frame.startswith('data:image'):
                    # Extract base64 data from the data URL
                    frame_data = frame.split(',')[1]
                    img_data = base64.b64decode(frame_data)
                    np_arr = np.frombuffer(img_data, np.uint8)
                    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )
                    
                    # If faces found, assign random emotion with weighted probabilities
                    # In a real implementation, this would use a trained ML model
                    if len(faces) > 0:
                        logger.info(f"Detected {len(faces)} faces in webcam frame")
                        weights = [0.1, 0.05, 0.1, 0.25, 0.15, 0.15, 0.2]  # weights for each emotion
                        emotion = random.choices(self.emotions, weights=weights, k=1)[0]
                        
                        # Only update emotion periodically to avoid rapid changes
                        current_time = time.time()
                        if current_time - self.last_detection_time > self.emotion_duration:
                            self.current_emotion = emotion
                            self.last_detection_time = current_time
                            logger.info(f"New webcam-detected emotion: {self.current_emotion}")
                        
                        return self.current_emotion
            except Exception as e:
                logger.error(f"Error processing webcam frame: {e}")
        
        # For demonstration purposes, change emotion periodically if not from webcam
        current_time = time.time()
        if current_time - self.last_detection_time > self.emotion_duration:
            # Weighted random selection - happy and neutral are more common
            weights = [0.1, 0.05, 0.1, 0.25, 0.15, 0.15, 0.2]  # weights for each emotion
            self.current_emotion = random.choices(self.emotions, weights=weights, k=1)[0]
            
            self.last_detection_time = current_time
            logger.debug(f"New auto-detected emotion: {self.current_emotion}")
        
        return self.current_emotion
