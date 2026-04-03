import time
import math
from modules.tts import TextToSpeech


class FallDetector:
    def __init__(self):
        self.tts = TextToSpeech()

        # Fall detection thresholds
        self.FALL_THRESHOLD = 2.5      # G-force threshold for fall
        self.TILT_THRESHOLD = 60       # Degrees tilt threshold

        self.simulation_mode = True    # Set False on Raspberry Pi
        self.fall_detected = False
        self.last_fall_time = 0
        self.cooldown = 10             # Seconds between fall alerts

        # Uncomment on Raspberry Pi:
        # self._setup_mpu6050()

    def _setup_mpu6050(self):
        """Initialize MPU6050 sensor on Raspberry Pi."""
        import smbus2
        self.bus = smbus2.SMBus(1)
        self.MPU6050_ADDR = 0x68
        # Wake up MPU6050
        self.bus.write_byte_data(self.MPU6050_ADDR, 0x6B, 0)
        print("[FallDetection] MPU6050 initialized.")

    def read_mpu6050(self):
        """Read accelerometer data from MPU6050."""
        import smbus2

        def read_word(addr):
            high = self.bus.read_byte_data(self.MPU6050_ADDR, addr)
            low = self.bus.read_byte_data(self.MPU6050_ADDR, addr + 1)
            val = (high << 8) + low
            if val >= 0x8000:
                val = -((65535 - val) + 1)
            return val

        ax = read_word(0x3B) / 16384.0
        ay = read_word(0x3D) / 16384.0
        az = read_word(0x3F) / 16384.0
        return ax, ay, az

    def simulate_reading(self, scenario='normal'):
        """Simulate IMU readings for laptop testing."""
        import random
        if scenario == 'fall':
            return (3.5, 3.2, 0.1)     # High G-force = fall
        elif scenario == 'tilt':
            return (0.1, 2.0, 0.3)     # Tilted
        else:
            return (                    # Normal walking
                random.uniform(-0.2, 0.2),
                random.uniform(-0.2, 0.2),
                random.uniform(0.9, 1.1)
            )

    def calculate_gforce(self, ax, ay, az):
        """Calculate total G-force magnitude."""
        return math.sqrt(ax**2 + ay**2 + az**2)

    def calculate_tilt(self, ax, ay, az):
        """Calculate tilt angle in degrees."""
        tilt = math.degrees(math.atan2(math.sqrt(ax**2 + ay**2), az))
        return abs(tilt)

    def detect(self, ax, ay, az):
        """Check if a fall has occurred."""
        gforce = self.calculate_gforce(ax, ay, az)
        tilt = self.calculate_tilt(ax, ay, az)

        print(f"[FallDetection] G-force: {gforce:.2f} | Tilt: {tilt:.1f}°")

        now = time.time()
        if now - self.last_fall_time < self.cooldown:
            return False

        if gforce > self.FALL_THRESHOLD or tilt > self.TILT_THRESHOLD:
            self.fall_detected = True
            self.last_fall_time = now
            print("[FallDetection] ⚠️ FALL DETECTED!")
            self.tts.speak("Fall detected! Sending SOS alert!")
            return True

        return False

    def run(self):
        """Continuously monitor for falls."""
        print("[FallDetection] Monitoring for falls...")
        scenarios = ['normal', 'normal', 'normal', 'fall', 'normal']
        i = 0

        try:
            while True:
                if self.simulation_mode:
                    scenario = scenarios[i % len(scenarios)]
                    ax, ay, az = self.simulate_reading(scenario)
                    i += 1
                else:
                    ax, ay, az = self.read_mpu6050()

                fall = self.detect(ax, ay, az)

                if fall:
                    print("[FallDetection] Triggering GPS SOS...")
                    # GPS SOS will be triggered from main.py

                time.sleep(0.5)

        except KeyboardInterrupt:
            print("[FallDetection] Stopped.")


# Quick test
if __name__ == "__main__":
    detector = FallDetector()
    detector.run()