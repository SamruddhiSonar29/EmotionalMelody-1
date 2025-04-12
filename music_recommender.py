import os
import json
import random
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MusicRecommender:
    """Class for recommending music based on detected emotions"""
    
    def __init__(self):
        """Initialize the music recommender with song library"""
        # Load music library
        self.music_library = self._load_music_library()
        logger.info("Music recommender initialized successfully")
        
    def _load_music_library(self):
        """Load the music library from JSON file"""
        try:
            with open('static/data/music_library.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logger.warning("Music library file not found. Creating default library.")
            # Create a default music library
            default_library = self._create_default_library()
            
            # Ensure directory exists
            os.makedirs('static/data', exist_ok=True)
            
            # Save the default library
            with open('static/data/music_library.json', 'w') as file:
                json.dump(default_library, file)
            
            return default_library
        except Exception as e:
            logger.error(f"Error loading music library: {e}")
            return self._create_default_library()
    
    def _create_default_library(self):
        """Create a default music library with popular songs for each emotion"""
        library = {
            "happy": {
                "english": [
                    {"title": "Happy", "artist": "Pharrell Williams", "youtube_id": "ZbZSe6N_BXs"},
                    {"title": "Can't Stop the Feeling", "artist": "Justin Timberlake", "youtube_id": "ru0K8uYEZWw"},
                    {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "youtube_id": "OPf0YbXqDm0"},
                    {"title": "Walking on Sunshine", "artist": "Katrina and The Waves", "youtube_id": "iPUmE-tne5U"}
                ],
                "hindi": [
                    {"title": "Badtameez Dil", "artist": "Benny Dayal", "youtube_id": "II2EO3Nw4m0"},
                    {"title": "Nagada Sang Dhol", "artist": "Shreya Ghoshal", "youtube_id": "X0peZpC8hx0"},
                    {"title": "London Thumakda", "artist": "Labh Janjua", "youtube_id": "udra42JzgAM"},
                    {"title": "Dil Dhadakne Do", "artist": "Priyanka Chopra", "youtube_id": "WvLT_L4pHxI"}
                ]
            },
            "sad": {
                "english": [
                    {"title": "Someone Like You", "artist": "Adele", "youtube_id": "hLQl3WQQoQ0"},
                    {"title": "Fix You", "artist": "Coldplay", "youtube_id": "k4V3Mo61fJM"},
                    {"title": "Let Her Go", "artist": "Passenger", "youtube_id": "RBumgq5yVrA"},
                    {"title": "All I Want", "artist": "Kodaline", "youtube_id": "mtf7hC17IBM"}
                ],
                "hindi": [
                    {"title": "Channa Mereya", "artist": "Arijit Singh", "youtube_id": "284Ov7ysmfA"},
                    {"title": "Tum Hi Ho", "artist": "Arijit Singh", "youtube_id": "Umqb9KENgmk"},
                    {"title": "Luka Chuppi", "artist": "A.R. Rahman", "youtube_id": "HcOc_eUpBbY"},
                    {"title": "Agar Tum Saath Ho", "artist": "Arijit Singh", "youtube_id": "sK7riqg2mr4"}
                ]
            },
            "angry": {
                "english": [
                    {"title": "Numb", "artist": "Linkin Park", "youtube_id": "kXYiU_JCYtU"},
                    {"title": "Enter Sandman", "artist": "Metallica", "youtube_id": "CD-E-LDc384"},
                    {"title": "Toxicity", "artist": "System of a Down", "youtube_id": "iywaBOMvYLI"},
                    {"title": "In The End", "artist": "Linkin Park", "youtube_id": "eVTXPUF4Oz4"}
                ],
                "hindi": [
                    {"title": "Jee Karda", "artist": "Divya Kumar", "youtube_id": "LFDXHsiwTVc"},
                    {"title": "Bhag Bhag DK Bose", "artist": "Ram Sampath", "youtube_id": "IQEDu8SPHao"},
                    {"title": "Chhu Kar Mere Man Ko", "artist": "Yesudas", "youtube_id": "fGJXXPI9hU0"},
                    {"title": "Sadda Haq", "artist": "Mohit Chauhan", "youtube_id": "p9DQINKZxWE"}
                ]
            },
            "neutral": {
                "english": [
                    {"title": "Perfect", "artist": "Ed Sheeran", "youtube_id": "2Vv-BfVoq4g"},
                    {"title": "Someone You Loved", "artist": "Lewis Capaldi", "youtube_id": "zABLecsR5UE"},
                    {"title": "Shallow", "artist": "Lady Gaga, Bradley Cooper", "youtube_id": "bo_efYhYU2A"},
                    {"title": "Say You Won't Let Go", "artist": "James Arthur", "youtube_id": "0yW7w8F2TVA"}
                ],
                "hindi": [
                    {"title": "Iktara", "artist": "Amit Trivedi", "youtube_id": "fSS_R91Nimw"},
                    {"title": "Tum Se Hi", "artist": "Mohit Chauhan", "youtube_id": "NXmN-Y2YeeI"},
                    {"title": "Kun Faya Kun", "artist": "A.R. Rahman", "youtube_id": "T94PHkuydcw"},
                    {"title": "Kabira", "artist": "Arijit Singh", "youtube_id": "jHNNMj5bNQw"}
                ]
            },
            "surprise": {
                "english": [
                    {"title": "What Makes You Beautiful", "artist": "One Direction", "youtube_id": "QJO3ROT-A4E"},
                    {"title": "Shape of You", "artist": "Ed Sheeran", "youtube_id": "JGwWNGJdvx8"},
                    {"title": "Don't Stop Believin'", "artist": "Journey", "youtube_id": "1k8craCGpgs"},
                    {"title": "I Gotta Feeling", "artist": "Black Eyed Peas", "youtube_id": "uSD4vsh1zDA"}
                ],
                "hindi": [
                    {"title": "Koi Mil Gaya", "artist": "Udit Narayan", "youtube_id": "lV4EGG2CwIQ"},
                    {"title": "Deewangi Deewangi", "artist": "Shaan", "youtube_id": "2eJTxiKrhQI"},
                    {"title": "Jumme Ki Raat", "artist": "Mika Singh", "youtube_id": "jY8WN1m4VVU"},
                    {"title": "It's The Time To Disco", "artist": "KK", "youtube_id": "_5mJAGXCiYQ"}
                ]
            },
            "fear": {
                "english": [
                    {"title": "Breathe Me", "artist": "Sia", "youtube_id": "SFGvmrJ5rjM"},
                    {"title": "Everybody's Changing", "artist": "Keane", "youtube_id": "RSNmgE6L8AU"},
                    {"title": "Fix You", "artist": "Coldplay", "youtube_id": "k4V3Mo61fJM"},
                    {"title": "Skinny Love", "artist": "Birdy", "youtube_id": "aNzCDt2eidg"}
                ],
                "hindi": [
                    {"title": "Darkhast", "artist": "Arijit Singh", "youtube_id": "0zAFpUriLRE"},
                    {"title": "Phir Le Aya Dil", "artist": "Arijit Singh", "youtube_id": "2jRATDHoHBQ"},
                    {"title": "Abhi Mujh Mein Kahin", "artist": "Sonu Nigam", "youtube_id": "oWKgpB2zpgw"},
                    {"title": "Zinda", "artist": "Amit Trivedi", "youtube_id": "cgHLvt0rxVs"}
                ]
            },
            "disgust": {
                "english": [
                    {"title": "Stronger", "artist": "Kelly Clarkson", "youtube_id": "Xn676-fLq7I"},
                    {"title": "Fighter", "artist": "Christina Aguilera", "youtube_id": "PstrAfoMKlc"},
                    {"title": "So What", "artist": "P!nk", "youtube_id": "FJfFZqTlWrQ"},
                    {"title": "I Don't Care", "artist": "Ed Sheeran & Justin Bieber", "youtube_id": "CCSGelSCPGE"}
                ],
                "hindi": [
                    {"title": "Beech Beech Mein", "artist": "Arijit Singh", "youtube_id": "ePTNDJUCz-o"},
                    {"title": "Gulaabo", "artist": "Vishal Dadlani", "youtube_id": "bVb1BUG22Lc"},
                    {"title": "Tarefan", "artist": "Badshah", "youtube_id": "crttU0yyZ4w"},
                    {"title": "Ud-daa Punjab", "artist": "Amit Trivedi", "youtube_id": "QzfsGxrCD4o"}
                ]
            }
        }
        
        return library

    def recommend_song(self, emotion, language='english'):
        """Recommend a single song based on detected emotion and language preference"""
        songs = self.recommend_songs(emotion, language, count=1)
        if songs and len(songs) > 0:
            return songs[0]
        else:
            # Return a default song if there's an error
            return {
                'title': "Happy",
                'artist': "Pharrell Williams",
                'youtube_id': "ZbZSe6N_BXs",
                'emotion': "neutral",
                'language': language.lower()
            }
    
    def recommend_songs(self, emotion, language='english', count=5):
        """Recommend multiple songs based on detected emotion and language preference"""
        # Map similar emotions if not directly found in the library
        emotion_map = {
            "angry": "angry",
            "disgust": "disgust",
            "fear": "fear",
            "happy": "happy",
            "sad": "sad",
            "surprise": "surprise",
            "neutral": "neutral"
        }
        
        # Map to available emotion category or default to neutral
        mapped_emotion = emotion_map.get(emotion.lower(), "neutral")
        
        # Validate language
        if language.lower() not in ['english', 'hindi']:
            language = 'english'
        
        try:
            # Get songs for the emotion and language
            available_songs = self.music_library[mapped_emotion][language.lower()]
            
            # Return up to 'count' songs (or shuffle and return all if fewer are available)
            songs_to_return = []
            if len(available_songs) <= count:
                # If we have fewer songs than requested, shuffle and return all of them
                shuffled_songs = available_songs.copy()
                random.shuffle(shuffled_songs)
                songs_to_return = shuffled_songs
            else:
                # Otherwise, select random 'count' songs without duplicates
                songs_to_return = random.sample(available_songs, count)
            
            # Format each song with additional info
            formatted_songs = []
            for song in songs_to_return:
                formatted_songs.append({
                    'title': song['title'],
                    'artist': song['artist'],
                    'youtube_id': song['youtube_id'],
                    'emotion': mapped_emotion,
                    'language': language.lower()
                })
            
            return formatted_songs
            
        except (KeyError, IndexError) as e:
            logger.error(f"Error recommending songs: {e}")
            # Return empty list if there's an error
            return []
