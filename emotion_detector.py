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
        
        # Initialize with last detection time
        self.last_detection_time = time.time()
        self.current_emotion = 'neutral'
        self.emotion_duration = 7  # seconds to keep each emotion (increased for better UX)
        self.manual_mode = False   # Track if emotion was manually set
        self.manual_emotion = None # Store manually selected emotion
        
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
        
        # For demonstration purposes, change emotion periodically
        current_time = time.time()
        if current_time - self.last_detection_time > self.emotion_duration:
            # Weighted random selection - happy and neutral are more common
            weights = [0.1, 0.05, 0.1, 0.25, 0.15, 0.15, 0.2]  # weights for each emotion
            self.current_emotion = random.choices(self.emotions, weights=weights, k=1)[0]
            
            self.last_detection_time = current_time
            logger.debug(f"New auto-detected emotion: {self.current_emotion}")
        
        return self.current_emotion
