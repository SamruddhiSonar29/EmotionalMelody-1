import os
import logging
import cv2
import random
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
    
    while True:
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
        
        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logger.error("Failed to encode frame")
            continue
            
        # Yield the frame in bytes
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

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
