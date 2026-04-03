import pyttsx3
import threading

class TextToSpeech:
    def __init__(self, language='en'):
        self.engine = pyttsx3.init()
        self.language = language
        self._configure_engine()
        self._lock = threading.Lock()

    def _configure_engine(self):
        """Set voice speed and volume."""
        self.engine.setProperty('rate', 150)    # Speed (words per minute)
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

    def speak(self, text):
        """Speak text in a thread-safe way."""
        with self._lock:
            print(f"[TTS] Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()

    def speak_async(self, text):
        """Speak without blocking main program."""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

    def set_language(self, lang_code):
        """Change language (e.g. 'hi' for Hindi, 'en' for English)."""
        self.language = lang_code
        print(f"[TTS] Language set to: {lang_code}")

    def stop(self):
        """Stop speaking."""
        self.engine.stop()


# Quick test
if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak("VisionStick is ready. I will help you navigate safely.")
    tts.speak_async("Object detected. Person ahead, 2 meters.")
    import time
    time.sleep(3)