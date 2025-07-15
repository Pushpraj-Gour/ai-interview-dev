import speech_recognition as sr
import pyttsx3

# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize text-to-speech engine (optional for voice feedback)
engine = pyttsx3.init()

# Function to save text to a file (in English)
def save_text_to_file(text, filename="recognized_english_text.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Text saved to {filename}")

# Function to speak a message (optional for voice feedback)
def speak_message(message):
    engine.say(message)
    engine.runAndWait()

def listen_and_recognize():
    accumulated_text = ""
    print("Listening for English voice input. The program will stop after 3 seconds of silence.")

    while True:
        try:
            with sr.Microphone() as source:
                # Adjust the recognizer sensitivity to ambient noise
                recognizer.adjust_for_ambient_noise(source)

                print("Listening...")

                # Listen to the audio, with a phrase time limit of 3 seconds of silence
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)

                # Recognize speech using Google Web Speech API in English ('en-US')
                recognized_text = recognizer.recognize_google(audio, language="en-US")

                print(f"You said: {recognized_text}")
                accumulated_text += recognized_text + " "
        
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Network error: {e}")
        except sr.WaitTimeoutError:
            print("No voice detected, stopping.")
            speak_message("Stopping the recording.")  # Optional feedback
            break

    # Save the accumulated text (in English) to a file
    save_text_to_file(accumulated_text)

# Start the voice recognition process
listen_and_recognize()
