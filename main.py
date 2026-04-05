import cv2
import threading
import time
import sys

from modules.tts import TextToSpeech
from modules.object_detection import ObjectDetector
from modules.obstacle_alert import ObstacleAlert
from modules.ocr_reader import OCRReader
from modules.fall_detection import FallDetector
from modules.gps_sos import GPSSOS
from modules.navigation import Navigation
from modules.multilingual import MultilingualSupport


class VisionStick:
    def __init__(self, language='en'):
        print("=" * 50)
        print("   VisionStick — AI Blind Assistance System")
        print("   GLA University | B.Tech CS (AI/ML) 2025")
        print("=" * 50)

        # Initialize all modules
        print("\n[VisionStick] Initializing modules...")
        self.ml = MultilingualSupport(default_language=language)
        self.tts = TextToSpeech()
        self.detector = ObjectDetector()
        self.obstacle = ObstacleAlert()
        self.ocr = OCRReader()
        self.fall = FallDetector()
        self.gps = GPSSOS()
        self.nav = Navigation()

        # State
        self.running = False
        self.language = language
        self.ocr_enabled = True
        self.nav_active = False
        self.last_ocr_scan = 0
        self.ocr_interval = 5       # Scan for text every 5 seconds

        print("[VisionStick] All modules initialized! ✅")

    def startup_announce(self):
        """Announce startup in user's language."""
        self.ml.set_language(self.language)
        self.ml.speak('ready')
        time.sleep(1)
        self.tts.speak("All systems online. Camera active.")

    def handle_fall(self):
        """Called when fall is detected."""
        print("[VisionStick] ⚠️ Fall detected! Triggering SOS...")
        self.ml.speak('fall_detected')
        time.sleep(1)
        self.gps.trigger_sos()

    def obstacle_monitor(self):
        """Run obstacle detection in background thread."""
        print("[VisionStick] Obstacle monitor started.")
        while self.running:
            front, ground = self.obstacle.check()

            # Alert based on distance
            if front < 50:
                self.ml.speak('obstacle_close')
            elif front < 100:
                self.ml.speak('obstacle_warning')
            if ground < 50:
                self.ml.speak('pothole')

            time.sleep(0.5)

    def fall_monitor(self):
        """Run fall detection in background thread."""
        print("[VisionStick] Fall monitor started.")
        while self.running:
            if self.fall.simulation_mode:
                ax, ay, az = self.fall.simulate_reading('normal')
            else:
                ax, ay, az = self.fall.read_mpu6050()

            if self.fall.detect(ax, ay, az):
                self.handle_fall()

            time.sleep(0.5)

    def run(self):
        """Main loop — camera + all features."""
        self.running = True
        self.startup_announce()

        # Start background threads
        obstacle_thread = threading.Thread(target=self.obstacle_monitor)
        obstacle_thread.daemon = True
        obstacle_thread.start()

        fall_thread = threading.Thread(target=self.fall_monitor)
        fall_thread.daemon = True
        fall_thread.start()

        # Start camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[VisionStick] ❌ Camera not found!")
            self.tts.speak("Camera not found. Please check connection.")
            return

        print("[VisionStick] 🎥 Camera active. Press Q to quit.")
        print("[VisionStick] Controls:")
        print("  Q = Quit")
        print("  O = Toggle OCR")
        print("  S = Trigger SOS")
        print("  N = Start Navigation")
        print("  H = Switch to Hindi")
        print("  E = Switch to English")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            now = time.time()

            # Object Detection
            detections = self.detector.detect(frame)

            # Auto OCR every 5 seconds
            if self.ocr_enabled and (now - self.last_ocr_scan > self.ocr_interval):
                texts = self.ocr.read_frame(frame)
                if texts:
                    combined = ". ".join([t['text'] for t in texts])
                    self.ml.speak_text(f"Text: {combined}")
                self.last_ocr_scan = now

            # Draw detections on screen
            for det in detections:
                x1, y1, x2, y2 = det['box']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{det['label']} {det['distance']}",
                           (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Status overlay
            cv2.putText(frame, f"VisionStick | Lang: {self.language.upper()}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "Q=Quit | O=OCR | S=SOS | N=Nav | H=Hindi | E=English",
                       (10, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cv2.imshow('VisionStick', frame)

            # Keyboard controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("[VisionStick] Shutting down...")
                break
            elif key == ord('o'):
                self.ocr_enabled = not self.ocr_enabled
                status = "enabled" if self.ocr_enabled else "disabled"
                self.tts.speak(f"OCR {status}")
            elif key == ord('s'):
                self.gps.trigger_sos()
            elif key == ord('n'):
                destination = "GLA University Main Gate"
                self.nav.navigate_to(destination)
            elif key == ord('h'):
                self.language = 'hi'
                self.ml.set_language('hi')
                self.ml.speak('ready')
            elif key == ord('e'):
                self.language = 'en'
                self.ml.set_language('en')
                self.ml.speak('ready')

        self.running = False
        cap.release()
        cv2.destroyAllWindows()
        print("[VisionStick] Goodbye!")
        self.tts.speak("VisionStick shutting down. Stay safe!")


def main():
    # Default language from command line argument
    language = 'en'
    if len(sys.argv) > 1:
        language = sys.argv[1]

    stick = VisionStick(language=language)
    stick.run()


if __name__ == "__main__":
    main()