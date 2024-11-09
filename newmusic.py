import os
import speech_recognition as sr
import tempfile
import yt_dlp
import pygame
from gtts import gTTS
import time
from youtube_search import YoutubeSearch

class MusicPlayer:
    def __init__(self):
        """Initialize the music player"""
        self.recognizer = sr.Recognizer()
        self.temp_dir = tempfile.mkdtemp()
        pygame.mixer.init()
        
    def recognize_speech(self):
        """Listen for and recognize speech input"""
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                print("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                print("Could not request results from speech recognition service")
                return None

    def speak(self, text):
        """Convert text to speech and play it"""
        tts = gTTS(text=text, lang='en')
        temp_file = os.path.join(self.temp_dir, 'response.mp3')
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        try:
            os.remove(temp_file)
        except:
            pass

    def get_video_id(self, query):
        """Search YouTube and return the first video ID"""
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            if results:
                return results[0]['id']
            return None
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None

    def get_video_title(self, url):
        """Get the title of a YouTube video"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info.get('title', '')
            except:
                return ''

    def get_audio_url(self, url):
        """Get the audio URL for a YouTube video"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_audio': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info['url']
            except Exception as e:
                print(f"Error extracting audio URL: {e}")
                return None

    def play_audio(self, url):
        """Play audio from URL"""
        # Download the audio file
        temp_file = os.path.join(self.temp_dir, 'music.mp3')
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': temp_file,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Play the audio
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Cleanup
        try:
            os.remove(temp_file)
        except:
            pass

    def stop_current_playback(self):
        """Stop any current audio playback"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def cleanup(self):
        """Clean up temporary directory"""
        try:
            os.rmdir(self.temp_dir)
        except:
            pass

    def run(self):
        """Main execution flow"""
        while True:  # Add infinite loop
            try:
                # Stop any current playback
                self.stop_current_playback()
                
                # Get speech input
                audio_input = self.recognize_speech()
                if not audio_input:
                    self.speak("I didn't catch that, please try again")
                    continue  # Skip rest of loop and try again
                    
                # Confirm what was heard    
                self.speak(f"Playing {audio_input}")
                
                # Get video details and play
                video_id = self.get_video_id(audio_input) 
                if not video_id:
                    self.speak("No video found, please try again")
                    continue  # Skip rest of loop and try again
                    
                youtube_url = f"https://youtube.com/watch?v={video_id}"
                audio_url = self.get_audio_url(youtube_url)
                if not audio_url:
                    self.speak("Could not get audio, please try again")
                    continue
                    
                title = self.get_video_title(youtube_url)
                
                # Play audio
                self.play_audio(audio_url)
                
            except Exception as e:
                print(f"Error: {str(e)}")
                self.speak("Sorry, there was an error. Please try again")
            finally:
                self.cleanup()

if __name__ == "__main__":
    player = MusicPlayer()
    player.run()
