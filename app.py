import os
import logging
import cv2
import random
import time
import numpy as np
from flask import Flask, render_template, Response, jsonify, request
from emotion_detector import EmotionDetector
from music_recommender import MusicRecommender

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Initialize emotion detector and music recommender
emotion_detector = EmotionDetector()
music_recommender = MusicRecommender()

# Global variables
camera = None
detected_emotion = "neutral"
current_language = "english"
current_song = None

def get_camera():
    """Initialize or return the existing camera object"""
    global camera
    if camera is None:
        logger.info("Initializing camera...")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            logger.warning("Cannot access real camera, using simulated camera...")
            # We will just return a dummy camera object, but generate_frames will handle this case
            # by creating simulated frames
        else:
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera

def release_camera():
    """Release camera resources"""
    global camera
    if camera is not None:
        logger.info("Releasing camera...")
        camera.release()
        camera = None

def generate_frames():
    """Generate frames from webcam with emotion detection"""
    global detected_emotion
    
    cam = get_camera()
    
    # Check if this is a real camera or we need to simulate one
    use_simulated_camera = not cam.isOpened()
    
    if use_simulated_camera:
        logger.info("Using simulated camera feed")
    
    frame_count = 0
    
    while True:
        if use_simulated_camera:
            # Create a blank frame with a colored gradient background
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Create a gradient background
            for y in range(480):
                for x in range(640):
                    # Simple gradient from blue to green
                    blue = int(255 * (1 - y / 480))
                    green = int(255 * (x / 640))
                    frame[y, x] = (blue, green, 100)  # BGR format
            
            # Add some animated elements
            frame_count += 1
            center_x = 320 + int(100 * np.sin(frame_count / 30))
            center_y = 240 + int(80 * np.cos(frame_count / 20))
            
            # Draw a face-like shape
            cv2.circle(frame, (center_x, center_y), 80, (0, 0, 255), -1)  # Head
            cv2.circle(frame, (center_x - 30, center_y - 20), 15, (255, 255, 255), -1)  # Left eye
            cv2.circle(frame, (center_x + 30, center_y - 20), 15, (255, 255, 255), -1)  # Right eye
            
            # Draw a mouth that changes based on emotion
            if detected_emotion in ['happy', 'surprise']:
                cv2.ellipse(frame, (center_x, center_y + 20), (40, 20), 0, 0, 180, (255, 255, 255), -1)
            elif detected_emotion in ['sad', 'fear']:
                cv2.ellipse(frame, (center_x, center_y + 40), (40, 20), 0, 180, 360, (255, 255, 255), -1)
            else:
                cv2.ellipse(frame, (center_x, center_y + 20), (40, 5), 0, 0, 180, (255, 255, 255), -1)
            
            # Simulate emotion detection by just letting emotion_detector do its time-based logic
            if random.random() < 0.2:  # 20% chance to update the emotion
                detected_emotion = emotion_detector.detect_emotion(frame)
                
            success = True
        else:
            # Use real webcam
            success, frame = cam.read()
            if not success:
                logger.error("Failed to capture frame from camera")
                break
            
            # Flip the frame horizontally for a more natural view
            frame = cv2.flip(frame, 1)
            
            # Detect emotion (not in every frame to reduce load)
            if random.random() < 0.3:  # 30% chance to process a frame
                detected_emotion = emotion_detector.detect_emotion(frame)
        
        # Add emotion text to frame
        cv2.putText(frame, f"Emotion: {detected_emotion}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add UI overlay
        cv2.putText(frame, "Emotion-Based Music Recommender", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logger.error("Failed to encode frame")
            continue
            
        # Yield the frame in bytes
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Add a slight delay to control frame rate
        time.sleep(0.05)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    """API endpoint to detect emotion and recommend song"""
    global detected_emotion, current_song, current_language
    
    # Get the language preference from the request
    language = request.json.get('language', 'english')
    current_language = language
    
    # Use the detected emotion to recommend a song
    song = music_recommender.recommend_song(detected_emotion, language)
    current_song = song
    
    return jsonify({
        'emotion': detected_emotion,
        'song': song
    })

@app.route('/toggle_language', methods=['POST'])
def toggle_language():
    """API endpoint to toggle language preference"""
    global current_language, current_song
    
    # Toggle between 'english' and 'hindi'
    current_language = 'hindi' if current_language == 'english' else 'english'
    
    # Get a new song recommendation based on the updated language
    if detected_emotion:
        current_song = music_recommender.recommend_song(detected_emotion, current_language)
    
    return jsonify({
        'language': current_language,
        'song': current_song
    })

@app.route('/get_current_state')
def get_current_state():
    """API endpoint to get the current state of the app"""
    return jsonify({
        'emotion': detected_emotion,
        'language': current_language,
        'song': current_song
    })

@app.teardown_appcontext
def cleanup(exception=None):
    """Clean up resources when app context ends"""
    release_camera()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
