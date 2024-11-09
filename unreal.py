import speech_recognition as sr
import pyttsx3
import time
import subprocess
import os
from gtts import gTTS
import pygame
import tempfile

# Initialize pygame mixer for audio
pygame.mixer.init()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Get the absolute path to the project directory
PROJECT_DIR = os.path.expanduser('~/project/Smart_Cap')
VENV_PYTHON = os.path.expanduser('~/project/piper/.venv/bin/python3')
DETECT_PYTHON = os.path.expanduser('~/project/DETECT/examples/tf/bin/python3')

def listen(recognizer):
    """
    Listen for audio input and convert to text.
    Args:
        recognizer: Speech recognition object
    Returns:
        str: Recognized text or None if recognition failed
    """
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)
            try:
                command = recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None
    except Exception as e:
        print(f"Error during listening: {e}")
        return None

def speak_fast(text):
    """
    Quickly converts text to speech using gTTS and pygame
    Args:
        text (str): The text that will be spoken
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts = gTTS(text=text, lang='en')
        tts.save(fp.name)
        pygame.mixer.music.load(fp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        os.unlink(fp.name)

def speak(text):
    """
    Converts the provided text to speech.
    Args:
        text (str): The text that will be spoken.
    """
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()
    time.sleep(1)

def run_subprocess(python_path, script_path, cwd=None, additional_args=None):
    """
    Runs a subprocess with proper error handling.
    Args:
        python_path (str): Path to Python interpreter
        script_path (str): Path to script to run
        cwd (str): Working directory for the subprocess
        additional_args (list): Additional command line arguments
    """
    try:
        cmd = [python_path, script_path]
        if additional_args:
            cmd.extend(additional_args)
        process = subprocess.Popen(
            cmd,
            cwd=cwd or PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"Exception running {script_path}: {str(e)}")
        return None

def main():
    speak_fast("What would you like me to assist you with?")
    while True:
        command = listen(recognizer)
        if command:
            if "play" in command:
                speak("Playing music")
                run_subprocess(
                    VENV_PYTHON,
                    os.path.join(PROJECT_DIR, 'music.py')
                )
            elif "ai" in command:
                speak("Starting AI conversation")
                run_subprocess(
                    VENV_PYTHON,
                    os.path.join(PROJECT_DIR, 'assi.py')
                )
            elif "detect" in command:
                speak("Object detection mode on")
                run_subprocess(
                    DETECT_PYTHON,
                    'detect.py',
                    cwd=PROJECT_DIR,
                    additional_args=['--model', 'efficientdet_lite0.tflite']
                )
            elif "guide" in command:
                speak("Guiding routes mode on")
                run_subprocess(
                    VENV_PYTHON,
                    os.path.join(PROJECT_DIR, 'guide.py')
                )
            elif "bye" in command:
                speak("Turning off")
                break
            else:
                speak("Command not recognized, please try again.")

if __name__ == "__main__":
    main()
