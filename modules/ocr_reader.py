import easyocr
import cv2
import time
from modules.tts import TextToSpeech


class OCRReader:
    def __init__(self, languages=['en']):
        print("[OCR] Loading EasyOCR model...")
        self.reader = easyocr.Reader(languages, gpu=False)
        self.tts = TextToSpeech()
        self.last_spoken = ""
        self.last_spoken_time = 0
        self.cooldown = 5           # Seconds between same text alerts
        self.confidence_threshold = 0.4
        print("[OCR] Ready!")

    def read_frame(self, frame):
        """Extract text from a single frame."""
        results = self.reader.readtext(frame)
        texts = []

        for (bbox, text, confidence) in results:
            if confidence >= self.confidence_threshold:
                texts.append({
                    'text': text.strip(),
                    'confidence': round(confidence, 2)
                })
                print(f"[OCR] Detected: '{text}' (confidence: {confidence:.2f})")

        return texts

    def should_speak(self, text):
        """Avoid repeating same text too frequently."""
        now = time.time()
        if text != self.last_spoken or (now - self.last_spoken_time) > self.cooldown:
            self.last_spoken = text
            self.last_spoken_time = now
            return True
        return False

    def speak_texts(self, texts):
        """Speak all detected texts."""
        if not texts:
            return
        combined = ". ".join([t['text'] for t in texts])
        if self.should_speak(combined):
            self.tts.speak_async(f"Text detected: {combined}")

    def run_camera(self):
        """Run live OCR from webcam."""
        cap = cv2.VideoCapture(0)
        print("[OCR] Starting camera... Press Q to quit, S to scan.")
        last_scan = 0
        scan_interval = 3           # Scan every 3 seconds

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[OCR] Camera error!")
                break

            now = time.time()
            cv2.putText(frame, "Press S to scan text",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 255, 255), 2)

            # Auto scan every 3 seconds
            if now - last_scan > scan_interval:
                texts = self.read_frame(frame)
                self.speak_texts(texts)
                last_scan = now

                # Draw detected text on frame
                for t in texts:
                    cv2.putText(frame, t['text'],
                               (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                               0.8, (0, 255, 0), 2)

            cv2.imshow('VisionStick - OCR Reader', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                texts = self.read_frame(frame)
                self.speak_texts(texts)
                last_scan = now

        cap.release()
        cv2.destroyAllWindows()


# Quick test
if __name__ == "__main__":
    ocr = OCRReader(languages=['en'])
    ocr.run_camera()