import os
import logging
import random
from flask import Flask, render_template, jsonify, request, redirect, url_for
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
detected_emotion = "neutral"
current_language = "english"
current_song = None

# Use a simplified implementation without video streaming for better stability
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

# Added to prevent 404 errors if there are any legacy references to video_feed
@app.route('/video_feed')
def video_feed():
    """Redirect to index if this endpoint is called"""
    return redirect(url_for('index'))

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    """API endpoint to detect emotion and recommend songs"""
    global detected_emotion, current_song, current_language
    
    # Get the language preference from the request
    language = request.json.get('language', 'english')
    current_language = language
    
    # Get the frame data for webcam processing if available
    frame_data = request.json.get('frame')
    
    # Detect emotion (either from webcam frame or using simulated approach)
    if frame_data:
        # If we have frame data, use it for emotion detection
        detected_emotion = emotion_detector.detect_emotion(frame_data)
        logger.info(f"Emotion detected from webcam: {detected_emotion}")
    else:
        # In the simplified version, use the built-in random emotion generator
        # This simulates what the emotion detector would do
        if random.random() < 0.3:  # 30% chance to change emotion
            emotions = ['happy', 'sad', 'angry', 'neutral', 'surprise', 'fear', 'disgust']
            weights = [0.25, 0.15, 0.1, 0.2, 0.15, 0.05, 0.1]  # weighted probabilities
            detected_emotion = random.choices(emotions, weights=weights)[0]
            logger.info(f"New simulated emotion: {detected_emotion}")
    
    # Use the detected emotion to recommend multiple songs
    songs = music_recommender.recommend_songs(detected_emotion, language, count=5)
    
    # Store the first song as current song for backward compatibility
    if songs and len(songs) > 0:
        current_song = songs[0]
    else:
        current_song = None
    
    return jsonify({
        'emotion': detected_emotion,
        'songs': songs
    })

@app.route('/set_emotion', methods=['POST'])
def set_emotion():
    """API endpoint to manually set the emotion"""
    global detected_emotion, current_song, current_language
    
    emotion = request.json.get('emotion', 'neutral')
    language = request.json.get('language', current_language)
    current_language = language
    
    # Use the new manual emotion setter method
    detected_emotion = emotion_detector.set_manual_emotion(emotion)
    
    # Get multiple song recommendations
    songs = music_recommender.recommend_songs(detected_emotion, current_language, count=5)
    
    # Store the first song as current song for backward compatibility
    if songs and len(songs) > 0:
        current_song = songs[0]
        logger.info(f"Emotion manually set to {detected_emotion}, recommending {songs[0]['title']} and {len(songs)-1} more songs")
    else:
        current_song = None
        logger.info(f"Emotion manually set to {detected_emotion}, but no songs found")
    
    return jsonify({
        'emotion': detected_emotion,
        'songs': songs
    })

@app.route('/toggle_language', methods=['POST'])
def toggle_language():
    """API endpoint to toggle language preference"""
    global current_language, current_song
    
    # Toggle between 'english' and 'hindi'
    current_language = 'hindi' if current_language == 'english' else 'english'
    
    # Get new song recommendations based on the updated language
    if detected_emotion:
        songs = music_recommender.recommend_songs(detected_emotion, current_language, count=5)
        if songs and len(songs) > 0:
            current_song = songs[0]
        else:
            current_song = None
    else:
        songs = []
    
    return jsonify({
        'language': current_language,
        'songs': songs
    })

@app.route('/get_current_state')
def get_current_state():
    """API endpoint to get the current state of the app"""
    # Get fresh song recommendations based on current state
    songs = music_recommender.recommend_songs(detected_emotion, current_language, count=5)
    
    return jsonify({
        'emotion': detected_emotion,
        'language': current_language,
        'song': current_song,  # Keep for backward compatibility
        'songs': songs         # New field with multiple songs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
