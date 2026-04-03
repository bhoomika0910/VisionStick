import time
from modules.tts import TextToSpeech

# For Raspberry Pi, uncomment these:
# import RPi.GPIO as GPIO

class ObstacleAlert:
    def __init__(self):
        self.tts = TextToSpeech()

        # GPIO Pins (for Raspberry Pi)
        self.TRIG_FRONT = 23
        self.ECHO_FRONT = 24
        self.TRIG_GROUND = 27
        self.ECHO_GROUND = 22
        self.VIBRATION_PIN = 18

        # Thresholds in cm
        self.DANGER_DISTANCE = 50      # Less than 50cm = danger
        self.WARNING_DISTANCE = 100    # Less than 100cm = warning

        self.last_alert_time = 0
        self.cooldown = 2              # Seconds between alerts

        self.simulation_mode = True    # Set False on Raspberry Pi

        # Uncomment on Raspberry Pi:
        # self._setup_gpio()

    def _setup_gpio(self):
        """Initialize GPIO pins on Raspberry Pi."""
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG_FRONT, GPIO.OUT)
        GPIO.setup(self.ECHO_FRONT, GPIO.IN)
        GPIO.setup(self.TRIG_GROUND, GPIO.OUT)
        GPIO.setup(self.ECHO_GROUND, GPIO.IN)
        GPIO.setup(self.VIBRATION_PIN, GPIO.OUT)
        print("[ObstacleAlert] GPIO initialized.")

    def measure_distance(self, trig_pin, echo_pin):
        """Measure distance using HC-SR04 ultrasonic sensor."""
        import RPi.GPIO as GPIO

        GPIO.output(trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(trig_pin, False)

        start = time.time()
        stop = time.time()

        while GPIO.input(echo_pin) == 0:
            start = time.time()
        while GPIO.input(echo_pin) == 1:
            stop = time.time()

        elapsed = stop - start
        distance = (elapsed * 34300) / 2  # Convert to cm
        return round(distance, 2)

    def simulate_distance(self):
        """Simulate sensor readings for testing on laptop."""
        import random
        return random.choice([30, 45, 80, 120, 200])

    def vibrate(self, pattern='short'):
        """Trigger vibration motor on Raspberry Pi."""
        # Uncomment on Raspberry Pi:
        # import RPi.GPIO as GPIO
        # if pattern == 'short':
        #     GPIO.output(self.VIBRATION_PIN, True)
        #     time.sleep(0.2)
        #     GPIO.output(self.VIBRATION_PIN, False)
        # elif pattern == 'long':
        #     GPIO.output(self.VIBRATION_PIN, True)
        #     time.sleep(0.5)
        #     GPIO.output(self.VIBRATION_PIN, False)
        print(f"[ObstacleAlert] Vibration: {pattern}")

    def should_alert(self):
        """Check cooldown before alerting."""
        now = time.time()
        if now - self.last_alert_time > self.cooldown:
            self.last_alert_time = now
            return True
        return False

    def check(self):
        """Main check — reads sensors and triggers alerts."""
        if self.simulation_mode:
            front_dist = self.simulate_distance()
            ground_dist = self.simulate_distance()
        else:
            front_dist = self.measure_distance(self.TRIG_FRONT, self.ECHO_FRONT)
            ground_dist = self.measure_distance(self.TRIG_GROUND, self.ECHO_GROUND)

        print(f"[ObstacleAlert] Front: {front_dist}cm | Ground: {ground_dist}cm")

        if self.should_alert():
            # Front obstacle
            if front_dist < self.DANGER_DISTANCE:
                self.vibrate('long')
                self.tts.speak_async("Danger! Obstacle very close ahead!")
            elif front_dist < self.WARNING_DISTANCE:
                self.vibrate('short')
                self.tts.speak_async("Caution! Obstacle ahead.")

            # Ground obstacle / pothole
            if ground_dist < self.DANGER_DISTANCE:
                self.vibrate('long')
                self.tts.speak_async("Warning! Pothole or step ahead!")

        return front_dist, ground_dist

    def run(self):
        """Continuously monitor obstacles."""
        print("[ObstacleAlert] Starting obstacle monitoring...")
        try:
            while True:
                self.check()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("[ObstacleAlert] Stopped.")


# Quick test
if __name__ == "__main__":
    alert = ObstacleAlert()
    alert.run()