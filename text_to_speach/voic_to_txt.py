import speech_recognition as sr
import pyttsx3

# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize text-to-speech engine (optional)
engine = pyttsx3.init()

# Function to save text to a file
def save_text_to_file(text, filename="recognized_text.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Text saved to {filename}")

# Function to speak a message (optional for voice feedback)
def speak_message(message):
    engine.say(message)
    engine.runAndWait()

def listen_and_recognize():
    accumulated_text = ""
    
    print("Listening for voice input. Say 'stop' to end recording.")
    
    # Keep listening until "stop" is recognized
    while True:
        try:
            with sr.Microphone() as source:
                # Adjust the recognizer sensitivity to ambient noise
                recognizer.adjust_for_ambient_noise(source)
                
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                
                # Recognize speech using Google Web Speech API
                recognized_text = recognizer.recognize_google(audio, language="hi-IN")  # Using 'hi-IN' for Hindi
                
                print(f"You said: {recognized_text}")
                accumulated_text += recognized_text + " "

                # Check if the recognized text contains the word "stop" (can be in Hindi too)
                if "stop" in recognized_text.lower() or "स्टॉप" in recognized_text:
                    speak_message("Stopping and saving the text.")  # Optional voice feedback
                    break
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            print("Listening timeout reached.")

    # Save the accumulated text to a file
    save_text_to_file(accumulated_text)

# Start the voice recognition process
listen_and_recognize()
