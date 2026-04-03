import time
from modules.tts import TextToSpeech


class MultilingualSupport:
    def __init__(self, default_language='en'):
        self.tts = TextToSpeech()
        self.current_language = default_language

        # Supported languages
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'kn': 'Kannada'
        }

        # Translations for common VisionStick alerts
        self.translations = {
            'en': {
                'ready': 'VisionStick is ready',
                'person_ahead': 'Person ahead',
                'obstacle_close': 'Danger! Obstacle very close ahead!',
                'obstacle_warning': 'Caution! Obstacle ahead.',
                'pothole': 'Warning! Pothole or step ahead!',
                'fall_detected': 'Fall detected! Sending SOS alert!',
                'sos_sent': 'SOS alert sent to your caretaker!',
                'text_detected': 'Text detected',
                'arrived': 'You have reached your destination',
                'turn_right': 'Turn right',
                'turn_left': 'Turn left',
                'go_straight': 'Go straight',
            },
            'hi': {
                'ready': 'विज़नस्टिक तैयार है',
                'person_ahead': 'आगे व्यक्ति है',
                'obstacle_close': 'खतरा! आगे बाधा बहुत पास है!',
                'obstacle_warning': 'सावधान! आगे बाधा है।',
                'pothole': 'चेतावनी! आगे गड्ढा या सीढ़ी है!',
                'fall_detected': 'गिरना पता चला! SOS अलर्ट भेजा जा रहा है!',
                'sos_sent': 'SOS अलर्ट आपके देखभालकर्ता को भेजा गया!',
                'text_detected': 'टेक्स्ट पता चला',
                'arrived': 'आप अपने गंतव्य पर पहुंच गए हैं',
                'turn_right': 'दाएं मुड़ें',
                'turn_left': 'बाएं मुड़ें',
                'go_straight': 'सीधे जाएं',
            },
            'mr': {
                'ready': 'व्हिजनस्टिक तयार आहे',
                'person_ahead': 'पुढे माणूस आहे',
                'obstacle_close': 'धोका! पुढे अडथळा खूप जवळ आहे!',
                'obstacle_warning': 'सावधान! पुढे अडथळा आहे.',
                'pothole': 'इशारा! पुढे खड्डा किंवा पायरी आहे!',
                'fall_detected': 'पडणे आढळले! SOS अलर्ट पाठवला जात आहे!',
                'sos_sent': 'SOS अलर्ट तुमच्या काळजीवाहूला पाठवला!',
                'text_detected': 'मजकूर आढळला',
                'arrived': 'तुम्ही तुमच्या गंतव्यस्थानी पोहोचलात',
                'turn_right': 'उजवीकडे वळा',
                'turn_left': 'डावीकडे वळा',
                'go_straight': 'सरळ जा',
            }
        }

    def set_language(self, lang_code):
        """Change the active language."""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            lang_name = self.supported_languages[lang_code]
            print(f"[Multilingual] Language set to: {lang_name}")
            self.tts.set_language(lang_code)
            return True
        else:
            print(f"[Multilingual] ❌ Language '{lang_code}' not supported.")
            return False

    def get(self, key):
        """Get translated text for current language."""
        lang = self.current_language

        # Fall back to English if translation missing
        if lang not in self.translations:
            lang = 'en'

        text = self.translations[lang].get(key)
        if not text:
            # Fall back to English
            text = self.translations['en'].get(key, key)

        return text

    def speak(self, key):
        """Speak a translated message."""
        text = self.get(key)
        print(f"[Multilingual] [{self.current_language}] {text}")
        self.tts.speak_async(text)

    def translate_detection(self, label, position, distance):
        """Translate object detection alert."""
        # Basic translation of detection message
        if self.current_language == 'hi':
            return f"{label} {position} पर, {distance}"
        elif self.current_language == 'mr':
            return f"{label} {position} वर, {distance}"
        else:
            return f"{label} {position}, {distance}"

    def run(self):
        """Test multilingual support."""
        print("[Multilingual] Testing multilingual support...")

        # Test English
        self.set_language('en')
        self.speak('ready')
        time.sleep(2)

        # Test Hindi
        self.set_language('hi')
        self.speak('ready')
        time.sleep(2)

        # Test Marathi
        self.set_language('mr')
        self.speak('ready')
        time.sleep(2)

        print("[Multilingual] Test complete!")


# Quick test
if __name__ == "__main__":
    ml = MultilingualSupport()
    ml.run()