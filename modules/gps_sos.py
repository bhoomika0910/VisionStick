import time
import threading
from modules.tts import TextToSpeech


class GPSSOS:
    def __init__(self, telegram_token=None, caretaker_chat_id=None):
        self.tts = TextToSpeech()

        # Telegram Bot credentials
        # Get token from @BotFather on Telegram
        self.telegram_token = telegram_token or "YOUR_TELEGRAM_BOT_TOKEN"
        self.caretaker_chat_id = caretaker_chat_id or "YOUR_CHAT_ID"

        self.simulation_mode = True    # Set False on Raspberry Pi
        self.last_sos_time = 0
        self.cooldown = 30             # Seconds between SOS alerts

        # Uncomment on Raspberry Pi:
        # self._setup_gps()

    def _setup_gps(self):
        """Initialize Neo-6M GPS on Raspberry Pi."""
        import serial
        self.gps_serial = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
        print("[GPS] Neo-6M GPS initialized.")

    def get_gps_location(self):
        """Read real GPS coordinates from Neo-6M."""
        import serial
        import pynmea2

        while True:
            line = self.gps_serial.readline().decode('ascii', errors='replace')
            if line.startswith('$GPRMC') or line.startswith('$GNRMC'):
                try:
                    msg = pynmea2.parse(line)
                    if msg.status == 'A':  # A = Active/Valid fix
                        return msg.latitude, msg.longitude
                except pynmea2.ParseError:
                    continue
        return None, None

    def simulate_location(self):
        """Simulate GPS coordinates for laptop testing."""
        # GLA University, Mathura coordinates
        return 27.2090, 77.4977

    def send_telegram_sos(self, lat, lon):
        """Send SOS message with location to caretaker via Telegram."""
        try:
            import requests
            maps_link = f"https://maps.google.com/?q={lat},{lon}"
            message = (
                f"🆘 SOS ALERT - VisionStick User needs help!\n\n"
                f"📍 Location: {lat:.6f}, {lon:.6f}\n"
                f"🗺️ Google Maps: {maps_link}\n"
                f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            response = requests.post(url, json={
                'chat_id': self.caretaker_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            })

            if response.status_code == 200:
                print("[GPS SOS] ✅ Telegram SOS sent successfully!")
                return True
            else:
                print(f"[GPS SOS] ❌ Telegram error: {response.text}")
                return False

        except Exception as e:
            print(f"[GPS SOS] ❌ Error sending SOS: {e}")
            return False

    def trigger_sos(self):
        """Main SOS trigger — get location and send alert."""
        now = time.time()
        if now - self.last_sos_time < self.cooldown:
            print("[GPS SOS] SOS cooldown active, skipping.")
            return

        self.last_sos_time = now
        self.tts.speak_async("SOS alert being sent to your caretaker!")

        if self.simulation_mode:
            lat, lon = self.simulate_location()
            print(f"[GPS SOS] Simulated location: {lat}, {lon}")
        else:
            print("[GPS SOS] Getting GPS location...")
            lat, lon = self.get_gps_location()

        if lat and lon:
            print(f"[GPS SOS] Location: {lat}, {lon}")
            # Send in background thread
            thread = threading.Thread(
                target=self.send_telegram_sos,
                args=(lat, lon)
            )
            thread.daemon = True
            thread.start()
        else:
            print("[GPS SOS] ❌ Could not get GPS location!")
            self.tts.speak_async("Could not get location. Please call for help!")

    def run(self):
        """Test SOS trigger."""
        print("[GPS SOS] Testing SOS system...")
        self.trigger_sos()
        time.sleep(5)
        print("[GPS SOS] SOS test complete.")


# Quick test
if __name__ == "__main__":
    sos = GPSSOS()
    sos.run()