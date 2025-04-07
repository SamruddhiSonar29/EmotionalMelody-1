// Global variables
let languageToggle = 'english';
let emotionDetectionInterval = null;
let currentYoutubePlayer = null;

// Initialize the application when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, initializing application...');
    
    // Initialize webcam and emotion detection
    initializeApp();
    
    // Setup event listeners
    setupEventListeners();
});

// Initialize the application
function initializeApp() {
    // Get current state from the server
    fetch('/get_current_state')
        .then(response => response.json())
        .then(data => {
            console.log('Initial state:', data);
            
            // Update UI based on current state
            updateLanguageToggle(data.language);
            
            // If there's a current song, display it
            if (data.song) {
                displaySong(data.song);
            }
            
            // If there's a detected emotion, display it
            if (data.emotion) {
                updateEmotionDisplay(data.emotion);
            }
        })
        .catch(error => {
            console.error('Error getting initial state:', error);
        });
}

// Setup event listeners for buttons and controls
function setupEventListeners() {
    // Start detection button
    const startDetectionBtn = document.getElementById('start-detection');
    if (startDetectionBtn) {
        startDetectionBtn.addEventListener('click', toggleEmotionDetection);
    }
    
    // Language toggle button
    const toggleLanguageBtn = document.getElementById('toggle-language');
    if (toggleLanguageBtn) {
        toggleLanguageBtn.addEventListener('click', toggleLanguage);
    }
}

// Toggle emotion detection on/off
function toggleEmotionDetection() {
    const startBtn = document.getElementById('start-detection');
    const statusIndicator = document.getElementById('status-indicator');
    
    if (!emotionDetectionInterval) {
        // Start emotion detection
        startBtn.textContent = 'Stop Detection';
        startBtn.classList.remove('btn-primary');
        startBtn.classList.add('btn-danger');
        
        // Update status indicator
        statusIndicator.textContent = 'Active';
        statusIndicator.classList.remove('text-danger');
        statusIndicator.classList.add('text-success');
        
        // Start periodic emotion detection
        emotionDetectionInterval = setInterval(detectEmotion, 5000); // Every 5 seconds
        
        // Do an immediate detection
        detectEmotion();
        
    } else {
        // Stop emotion detection
        startBtn.textContent = 'Start Detection';
        startBtn.classList.remove('btn-danger');
        startBtn.classList.add('btn-primary');
        
        // Update status indicator
        statusIndicator.textContent = 'Inactive';
        statusIndicator.classList.remove('text-success');
        statusIndicator.classList.add('text-danger');
        
        // Clear the interval
        clearInterval(emotionDetectionInterval);
        emotionDetectionInterval = null;
    }
}

// Toggle language between English and Hindi
function toggleLanguage() {
    const toggleLanguageBtn = document.getElementById('toggle-language');
    
    // Toggle language via API
    fetch('/toggle_language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Language toggled:', data);
        
        // Update UI based on new language
        updateLanguageToggle(data.language);
        
        // Update song if one was returned
        if (data.song) {
            displaySong(data.song);
        }
    })
    .catch(error => {
        console.error('Error toggling language:', error);
    });
}

// Update language toggle button UI
function updateLanguageToggle(language) {
    const toggleLanguageBtn = document.getElementById('toggle-language');
    languageToggle = language;
    
    if (language === 'english') {
        toggleLanguageBtn.textContent = 'Switch to Hindi';
    } else {
        toggleLanguageBtn.textContent = 'Switch to English';
    }
}

// Detect emotion and get music recommendation
function detectEmotion() {
    console.log('Detecting emotion...');
    
    fetch('/detect_emotion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: languageToggle })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Emotion detected:', data);
        
        // Update emotion display
        updateEmotionDisplay(data.emotion);
        
        // Display recommended song
        if (data.song) {
            displaySong(data.song);
        }
    })
    .catch(error => {
        console.error('Error detecting emotion:', error);
    });
}

// Update emotion display in UI
function updateEmotionDisplay(emotion) {
    const emotionDisplay = document.getElementById('detected-emotion');
    if (emotionDisplay) {
        emotionDisplay.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
        
        // Update classes for emotion-specific styling
        const emotionClasses = ['emotion-happy', 'emotion-sad', 'emotion-angry', 
                               'emotion-neutral', 'emotion-surprise', 'emotion-fear', 'emotion-disgust'];
        
        emotionClasses.forEach(cls => {
            emotionDisplay.classList.remove(cls);
        });
        
        emotionDisplay.classList.add(`emotion-${emotion.toLowerCase()}`);
    }
}

// Display recommended song in UI
function displaySong(song) {
    const songTitle = document.getElementById('song-title');
    const songArtist = document.getElementById('song-artist');
    const playerContainer = document.getElementById('youtube-player');
    
    if (songTitle && songArtist) {
        songTitle.textContent = song.title;
        songArtist.textContent = song.artist;
    }
    
    // Update the YouTube player
    if (playerContainer && song.youtube_id) {
        // Remove any existing player
        playerContainer.innerHTML = '';
        
        // Create new iframe for YouTube player
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.youtube.com/embed/${song.youtube_id}?autoplay=1`;
        iframe.width = '100%';
        iframe.height = '300';
        iframe.frameBorder = '0';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.allowFullscreen = true;
        
        playerContainer.appendChild(iframe);
    }
}
