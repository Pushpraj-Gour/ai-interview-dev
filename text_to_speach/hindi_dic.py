from gtts import gTTS
import pygame
import io
import time

# List of Hindi words
hindi_words = ["नमस्ते", "आप", "कैसे", "हैं", "धन्यवाद"]
hindi_words = [
    "अदिति", "तरुण", "विद्या", "सौरभ", "अलका", "शिवांश", "ज्योति", "राहुल", "कृति", "नवीन",
    "अभिषेक", "मेघा", "रजनी", "विभोर", "शालिनी", "दीपेश", "सुधीर", "रक्षिता", "विराट", "प्रिया",
    "श्रवण", "ईशानी", "ध्रुव", "नेहा", "अवनी", "मनोज", "स्मिता", "उत्कर्ष", "प्रीति", "सुनील",
    "मोहित", "कौशिकी", "राकेश", "तृषा", "दिव्या", "कपिल", "नव्या", "विनय", "शिवानी", "विक्रम",
    "रोहित", "महक", "कैलाश", "अंकिता", "चेतन", "दर्पण", "ऋत्विक", "कुसुम", "हिमांशु", "वसुधा"
]



# hindi_words = hindi_words.split(", ")
# print(hindi_words)


# Set the language to Hindi ('hi' for Hindi)
language = 'hi'

# Time delay between words (in seconds)
delay = 4

# Initialize pygame mixer for sound playback
pygame.mixer.init()

# Function to speak each word
def speak_word(word):
    # Initialize gTTS object with the word and language
    tts = gTTS(text=word, lang=language, slow=False)

    # Use a BytesIO buffer to avoid saving to disk
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)  # Move to the start of the buffer
    
    # Load the audio data into pygame from the buffer
    pygame.mixer.music.load(audio_buffer, 'mp3')
    
    # Play the sound
    pygame.mixer.music.play()

    # Wait until the audio finishes playing
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

# Speak each word in the list with a delay
for word in hindi_words:
    speak_word(word)
    time.sleep(delay)  # Wait for the specified delay before speaking the next word
