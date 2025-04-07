import os
import logging
import random
from flask import Flask, render_template, jsonify, request
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

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    """API endpoint to detect emotion and recommend song"""
    global detected_emotion, current_song, current_language
    
    # Get the language preference from the request
    language = request.json.get('language', 'english')
    current_language = language
    
    # In the simplified version, we'll use a random emotion
    # This simulates what the emotion detector would do
    # without the performance overhead of video processing
    if random.random() < 0.3:  # 30% chance to change emotion
        emotions = ['happy', 'sad', 'angry', 'neutral', 'surprise', 'fear', 'disgust']
        weights = [0.25, 0.15, 0.1, 0.2, 0.15, 0.05, 0.1]  # weighted probabilities
        detected_emotion = random.choices(emotions, weights=weights)[0]
        logger.info(f"New simulated emotion: {detected_emotion}")
    
    # Use the detected emotion to recommend a song
    song = music_recommender.recommend_song(detected_emotion, language)
    current_song = song
    
    return jsonify({
        'emotion': detected_emotion,
        'song': song
    })

@app.route('/set_emotion', methods=['POST'])
def set_emotion():
    """API endpoint to manually set the emotion"""
    global detected_emotion, current_song, current_language
    
    emotion = request.json.get('emotion', 'neutral')
    detected_emotion = emotion
    
    # Update the song recommendation
    song = music_recommender.recommend_song(detected_emotion, current_language)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
