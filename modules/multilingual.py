import time
import os
import tempfile
import subprocess
from modules.tts import TextToSpeech


class MultilingualSupport:
    def __init__(self, default_language='en'):
        self.tts = TextToSpeech()
        self.current_language = default_language
        self.ffplay_path = r'C:\ffmpeg\bin\ffplay.exe'  # Windows
        # On Raspberry Pi, change to: 'ffplay'

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

        self.gtts_languages = ['hi', 'mr', 'ta', 'te', 'bn', 'gu', 'kn']

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
                'low_battery': 'Battery is low, please charge soon',
                'crowd_ahead': 'Crowded area ahead, move slowly',
                'low_light': 'Low light ahead, be careful',
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
                'low_battery': 'बैटरी कम है, कृपया चार्ज करें',
                'crowd_ahead': 'आगे भीड़ है, धीरे चलें',
                'low_light': 'आगे अंधेरा है, सावधान रहें',
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
                'low_battery': 'बॅटरी कमी आहे, कृपया चार्ज करा',
                'crowd_ahead': 'पुढे गर्दी आहे, हळू चला',
                'low_light': 'पुढे अंधार आहे, काळजी घ्या',
            },
            'ta': {
                'ready': 'விஷன்ஸ்டிக் தயாராக உள்ளது',
                'person_ahead': 'முன்னால் நபர் உள்ளார்',
                'obstacle_close': 'ஆபத்து! முன்னால் தடை மிக அருகில் உள்ளது!',
                'obstacle_warning': 'எச்சரிக்கை! முன்னால் தடை உள்ளது.',
                'fall_detected': 'விழுவது கண்டறியப்பட்டது! SOS அலர்ட் அனுப்பப்படுகிறது!',
                'arrived': 'நீங்கள் உங்கள் இலக்கை அடைந்துவிட்டீர்கள்',
                'turn_right': 'வலதுபுறம் திரும்பவும்',
                'turn_left': 'இடதுபுறம் திரும்பவும்',
                'go_straight': 'நேராக செல்லவும்',
            }
        }

    def speak_gtts(self, text, lang_code):
        """Use gTTS + ffplay for non-English languages."""
        try:
            from gtts import gTTS
            print(f"[Multilingual] [{lang_code}] {text}")
            tts = gTTS(text=text, lang=lang_code, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                temp_file = f.name
            tts.save(temp_file)
            subprocess.run(
                [self.ffplay_path, '-nodisp', '-autoexit', temp_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            os.unlink(temp_file)
        except Exception as e:
            print(f"[Multilingual] gTTS error: {e}")
            self.tts.speak(text)

    def set_language(self, lang_code):
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            print(f"[Multilingual] Language set to: {self.supported_languages[lang_code]}")
            return True
        print(f"[Multilingual] Language '{lang_code}' not supported.")
        return False

    def get(self, key):
        lang = self.current_language
        if lang not in self.translations:
            lang = 'en'
        return self.translations[lang].get(key) or self.translations['en'].get(key, key)

    def speak(self, key):
        text = self.get(key)
        if self.current_language in self.gtts_languages:
            self.speak_gtts(text, self.current_language)
        else:
            print(f"[Multilingual] [en] {text}")
            self.tts.speak(text)

    def speak_text(self, text):
        if self.current_language in self.gtts_languages:
            self.speak_gtts(text, self.current_language)
        else:
            self.tts.speak(text)

    def translate_detection(self, label, position, distance):
        if self.current_language == 'hi':
            return f"{label} {position} पर, {distance}"
        elif self.current_language == 'mr':
            return f"{label} {position} वर, {distance}"
        else:
            return f"{label} {position}, {distance}"

    def run(self):
        print("[Multilingual] Testing multilingual support...")
        self.set_language('en')
        self.speak('ready')
        time.sleep(3)
        self.set_language('hi')
        self.speak('ready')
        time.sleep(3)
        self.set_language('mr')
        self.speak('ready')
        time.sleep(3)
        self.set_language('ta')
        self.speak('ready')
        time.sleep(3)
        print("[Multilingual] Test complete!")


if __name__ == "__main__":
    ml = MultilingualSupport()
    ml.run()