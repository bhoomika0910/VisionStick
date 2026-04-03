import cv2
from ultralytics import YOLO
from modules.tts import TextToSpeech
import time

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt', confidence=0.5):
        print("[ObjectDetection] Loading YOLOv8 model...")
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.tts = TextToSpeech()
        self.last_spoken = {}       # Avoid repeating same object too fast
        self.cooldown = 3           # Seconds between same object alerts

        # Priority objects for blind assistance
        self.priority_objects = [
            'person', 'car', 'truck', 'bus', 'motorcycle',
            'bicycle', 'dog', 'chair', 'dining table',
            'stairs', 'door', 'traffic light', 'stop sign'
        ]

    def estimate_distance(self, box_height, frame_height):
        """Rough distance estimate based on bounding box size."""
        ratio = box_height / frame_height
        if ratio > 0.6:
            return "very close"
        elif ratio > 0.3:
            return "2 meters"
        elif ratio > 0.15:
            return "4 meters"
        else:
            return "far away"

    def get_position(self, box_center_x, frame_width):
        """Determine if object is left, center or right."""
        ratio = box_center_x / frame_width
        if ratio < 0.35:
            return "on your left"
        elif ratio > 0.65:
            return "on your right"
        else:
            return "ahead"

    def should_speak(self, label):
        """Check cooldown to avoid repeating alerts."""
        now = time.time()
        if label not in self.last_spoken:
            self.last_spoken[label] = now
            return True
        if now - self.last_spoken[label] > self.cooldown:
            self.last_spoken[label] = now
            return True
        return False

    def detect(self, frame):
        """Run detection on a single frame."""
        results = self.model(frame, conf=self.confidence, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                label = self.model.names[int(box.cls)]
                confidence = float(box.conf)
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                box_height = y2 - y1
                box_center_x = (x1 + x2) / 2
                frame_height, frame_width = frame.shape[:2]

                distance = self.estimate_distance(box_height, frame_height)
                position = self.get_position(box_center_x, frame_width)

                detections.append({
                    'label': label,
                    'confidence': confidence,
                    'distance': distance,
                    'position': position,
                    'box': (x1, y1, x2, y2)
                })

                # Speak only priority objects
                if label in self.priority_objects and self.should_speak(label):
                    message = f"{label} {position}, {distance}"
                    print(f"[ObjectDetection] {message}")
                    self.tts.speak_async(message)

        return detections

    def run_camera(self):
        """Run live detection from webcam."""
        cap = cv2.VideoCapture(0)
        print("[ObjectDetection] Starting camera... Press Q to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ObjectDetection] Camera error!")
                break

            detections = self.detect(frame)

            # Draw boxes on frame
            for det in detections:
                x1, y1, x2, y2 = det['box']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{det['label']} {det['distance']}",
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.5, (0, 255, 0), 2)

            cv2.imshow('VisionStick - Object Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# Quick test
if __name__ == "__main__":
    detector = ObjectDetector()
    detector.run_camera()