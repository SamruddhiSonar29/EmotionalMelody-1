// Global variables
let languageToggle = 'english';
let emotionDetectionInterval = null;
let currentYoutubePlayer = null;
let frameCount = 0;

// Initialize the application when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, initializing application...');
    
    // Initialize app and emotion selection
    initializeApp();
    
    // Setup event listeners
    setupEventListeners();
    
    // Start animation loop for UI elements
    requestAnimationFrame(animateUI);
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
    
    // Emotion pill buttons - now these will actually set the emotion
    const emotionPills = document.querySelectorAll('.emotion-pill');
    emotionPills.forEach(pill => {
        pill.addEventListener('click', function() {
            const emotion = this.getAttribute('data-emotion');
            setEmotionManually(emotion);
        });
    });
    
    // Emotion cards - now these will actually set the emotion
    const emotionCards = document.querySelectorAll('.emotion-card');
    emotionCards.forEach(card => {
        // Visual effect on hover
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
        
        // Set emotion on click
        card.addEventListener('click', function() {
            const emotion = this.classList[1]; // The second class is the emotion name
            setEmotionManually(emotion);
        });
    });
}

// Animate UI elements - optimized for performance
function animateUI() {
    frameCount++;
    
    // Only run animations every other frame to improve performance
    if (frameCount % 2 === 0) {
        // Pulse effect for active status dot
        const statusDot = document.querySelector('.status-dot.active');
        if (statusDot) {
            const pulseIntensity = Math.sin(frameCount * 0.05) * 0.3 + 0.7;
            statusDot.style.opacity = pulseIntensity;
        }
        
        // Subtle floating animation for emotion display - only run this animation
        // at a reduced frequency (every 4 frames)
        if (frameCount % 4 === 0) {
            const emotionDisplay = document.getElementById('emotion-display');
            if (emotionDisplay) {
                const floatOffset = Math.sin(frameCount * 0.01) * 2;
                emotionDisplay.style.transform = `translateY(${floatOffset}px)`;
            }
        }
    }
    
    // Continue animation loop
    requestAnimationFrame(animateUI);
}

// Toggle emotion detection on/off (auto or manual)
function toggleEmotionDetection() {
    const startBtn = document.getElementById('start-detection');
    const statusIndicator = document.getElementById('status-indicator');
    const statusDot = document.getElementById('status-dot');
    
    if (!emotionDetectionInterval) {
        // Start emotion detection
        startBtn.querySelector('span').textContent = 'Stop Auto Detection';
        startBtn.querySelector('i').classList.remove('fa-play-circle');
        startBtn.querySelector('i').classList.add('fa-stop-circle');
        startBtn.classList.add('active');
        
        // Update status indicator
        statusIndicator.textContent = 'Auto Mode';
        statusIndicator.classList.add('active');
        statusDot.classList.add('active');
        
        // Add active class to emotion cards
        document.querySelectorAll('.emotion-card, .emotion-pill').forEach(el => {
            el.classList.add('auto-mode');
        });
        
        // Add helper text
        const emotionCardsContainer = document.querySelector('.emotions-showcase');
        if (emotionCardsContainer && !document.querySelector('.auto-mode-notice')) {
            const notice = document.createElement('div');
            notice.className = 'auto-mode-notice';
            notice.innerHTML = '<p>Auto-detection is active. You can still click on emotions to manually select them.</p>';
            emotionCardsContainer.prepend(notice);
        }
        
        // Start periodic emotion detection
        emotionDetectionInterval = setInterval(detectEmotion, 7000);
        
        // Do an immediate detection
        detectEmotion();
        
    } else {
        // Stop emotion detection
        startBtn.querySelector('span').textContent = 'Start Auto Detection';
        startBtn.querySelector('i').classList.remove('fa-stop-circle');
        startBtn.querySelector('i').classList.add('fa-play-circle');
        startBtn.classList.remove('active');
        
        // Update status indicator
        statusIndicator.textContent = 'Manual Mode';
        statusIndicator.classList.remove('active');
        statusDot.classList.remove('active');
        
        // Remove active class from emotion cards
        document.querySelectorAll('.emotion-card, .emotion-pill').forEach(el => {
            el.classList.remove('auto-mode');
        });
        
        // Remove helper text
        const notice = document.querySelector('.auto-mode-notice');
        if (notice) {
            notice.remove();
        }
        
        // Clear the interval
        clearInterval(emotionDetectionInterval);
        emotionDetectionInterval = null;
    }
}

// Toggle language between English and Hindi
function toggleLanguage() {
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
    const languageLabels = toggleLanguageBtn.querySelectorAll('.language-label');
    
    languageToggle = language;
    
    // Update the visual state of the toggle button
    if (language === 'english') {
        // Highlight English, dim Hindi
        languageLabels[0].style.opacity = '1';
        languageLabels[0].style.fontWeight = 'bold';
        languageLabels[1].style.opacity = '0.5';
        languageLabels[1].style.fontWeight = 'normal';
    } else {
        // Highlight Hindi, dim English
        languageLabels[0].style.opacity = '0.5';
        languageLabels[0].style.fontWeight = 'normal';
        languageLabels[1].style.opacity = '1';
        languageLabels[1].style.fontWeight = 'bold';
    }
}

// Automatic emotion detection with server
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

// Set emotion manually when user clicks an emotion
function setEmotionManually(emotion) {
    console.log('Manually setting emotion to:', emotion);
    
    // Flash effect on selected emotion card
    highlightSelectedEmotion(emotion);
    
    // Send to server
    fetch('/set_emotion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            emotion: emotion,
            language: languageToggle
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Emotion set manually:', data);
        
        // Update emotion display
        updateEmotionDisplay(data.emotion);
        
        // Display recommended song
        if (data.song) {
            displaySong(data.song);
        }
    })
    .catch(error => {
        console.error('Error setting emotion:', error);
    });
}

// Highlight the selected emotion with a visual effect
function highlightSelectedEmotion(emotion) {
    // Find the emotion card
    const emotionCard = document.querySelector(`.emotion-card.${emotion}`);
    if (emotionCard) {
        // Add pulse effect
        emotionCard.classList.add('selected-pulse');
        
        // Remove after animation completes
        setTimeout(() => {
            emotionCard.classList.remove('selected-pulse');
        }, 1000);
    }
    
    // Find the pill too
    const emotionPill = document.querySelector(`.emotion-pill[data-emotion="${emotion}"]`);
    if (emotionPill) {
        // Add pulse effect
        emotionPill.classList.add('selected-pulse');
        
        // Remove after animation completes
        setTimeout(() => {
            emotionPill.classList.remove('selected-pulse');
        }, 1000);
    }
}

// Update emotion display in UI
function updateEmotionDisplay(emotion) {
    // Update the main emotion display
    const capitalizedEmotion = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    
    // Update text elements
    document.getElementById('detected-emotion').textContent = capitalizedEmotion;
    document.getElementById('detected-emotion-header').textContent = capitalizedEmotion;
    document.getElementById('track-emotion-tag').textContent = capitalizedEmotion;
    
    // Update emotion icon classes
    const emotionIcon = document.getElementById('emotion-icon');
    if (emotionIcon) {
        // Remove all emotion icon classes
        emotionIcon.className = 'emotion-icon';
        // Add the current emotion class
        emotionIcon.classList.add(`${emotion.toLowerCase()}-icon`);
    }
    
    // Set the appropriate icon in the emotion bubble
    updateEmotionBubble(emotion);
}

// Update the emotion bubble if it exists
function updateEmotionBubble(emotion) {
    const emotionBubble = document.getElementById('emotion-bubble');
    const emotionBubbleText = document.getElementById('emotion-bubble-text');
    const emotionBubbleIcon = document.querySelector('.emotion-bubble-icon');
    
    if (emotionBubble && emotionBubbleText && emotionBubbleIcon) {
        // Update text
        emotionBubbleText.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
        
        // Update icon
        emotionBubbleIcon.className = 'emotion-bubble-icon';
        
        // Set appropriate icon based on emotion
        switch(emotion.toLowerCase()) {
            case 'happy':
                emotionBubbleIcon.classList.add('fas', 'fa-smile');
                emotionBubble.style.borderColor = 'rgba(255, 209, 102, 0.5)';
                break;
            case 'sad':
                emotionBubbleIcon.classList.add('fas', 'fa-sad-tear');
                emotionBubble.style.borderColor = 'rgba(72, 145, 255, 0.5)';
                break;
            case 'angry':
                emotionBubbleIcon.classList.add('fas', 'fa-angry');
                emotionBubble.style.borderColor = 'rgba(255, 87, 87, 0.5)';
                break;
            case 'neutral':
                emotionBubbleIcon.classList.add('fas', 'fa-meh');
                emotionBubble.style.borderColor = 'rgba(170, 170, 170, 0.5)';
                break;
            case 'surprise':
                emotionBubbleIcon.classList.add('fas', 'fa-surprise');
                emotionBubble.style.borderColor = 'rgba(255, 102, 196, 0.5)';
                break;
            case 'fear':
                emotionBubbleIcon.classList.add('fas', 'fa-grimace');
                emotionBubble.style.borderColor = 'rgba(156, 119, 255, 0.5)';
                break;
            case 'disgust':
                emotionBubbleIcon.classList.add('fas', 'fa-dizzy');
                emotionBubble.style.borderColor = 'rgba(102, 255, 179, 0.5)';
                break;
            default:
                emotionBubbleIcon.classList.add('fas', 'fa-smile');
                emotionBubble.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        }
    }
}

// Display recommended song in UI
function displaySong(song) {
    const songTitle = document.getElementById('song-title');
    const songArtist = document.getElementById('song-artist');
    const playerContainer = document.getElementById('youtube-player');
    const emotionTag = document.getElementById('track-emotion-tag');
    
    if (songTitle && songArtist) {
        // Update song info
        songTitle.textContent = song.title;
        songArtist.textContent = song.artist;
    }
    
    // Update emotion tag if available
    if (emotionTag) {
        emotionTag.textContent = languageToggle.charAt(0).toUpperCase() + languageToggle.slice(1);
    }
    
    // Update the YouTube player
    if (playerContainer && song.youtube_id) {
        // Create a placeholder before the real player loads
        playerContainer.innerHTML = '<div class="player-loading"><div class="loading-spinner"></div><p>Loading music...</p></div>';
        
        // After a slight delay, create the real player
        setTimeout(() => {
            // Create new iframe for YouTube player
            const iframe = document.createElement('iframe');
            iframe.src = `https://www.youtube.com/embed/${song.youtube_id}?autoplay=1`;
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.borderRadius = '15px';
            iframe.style.border = 'none';
            iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            iframe.allowFullscreen = true;
            
            // Clear the container and add the iframe
            playerContainer.innerHTML = '';
            playerContainer.appendChild(iframe);
        }, 800);
    }
}

// Add custom styles for the manual emotion selection
const style = document.createElement('style');
style.textContent = `
.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.player-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-secondary);
}

.emotion-card, .emotion-pill {
    cursor: pointer;
    position: relative;
}

.emotion-card:hover, .emotion-pill:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.emotion-card.auto-mode, .emotion-pill.auto-mode {
    opacity: 0.8;
}

.emotion-card.auto-mode:after, .emotion-pill.auto-mode:after {
    content: 'Click to select';
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.7);
    padding: 3px 8px;
    border-radius: 8px;
    font-size: 10px;
    opacity: 0;
    transition: opacity 0.3s;
}

.emotion-card.auto-mode:hover:after, .emotion-pill.auto-mode:hover:after {
    opacity: 1;
}

.selected-pulse {
    animation: pulse-select 1s;
}

@keyframes pulse-select {
    0% {
        box-shadow: 0 0 0 0 rgba(140, 82, 255, 0.7);
    }
    70% {
        box-shadow: 0 0 0 15px rgba(140, 82, 255, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(140, 82, 255, 0);
    }
}

.auto-mode-notice {
    background-color: rgba(140, 82, 255, 0.1);
    border-left: 3px solid var(--primary-color);
    padding: 8px 15px;
    margin-bottom: 15px;
    border-radius: 5px;
    font-size: 0.9rem;
}
`;
document.head.appendChild(style);
