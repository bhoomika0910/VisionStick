import time
import requests
import threading
from modules.tts import TextToSpeech


class Navigation:
    def __init__(self):
        self.tts = TextToSpeech()
        self.simulation_mode = True
        self.is_navigating = False
        self.current_step = 0
        self.destination = None

        # OpenRouteService API (free, no billing needed)
        # Get free key at: https://openrouteservice.org/
        self.ORS_API_KEY = "YOUR_ORS_API_KEY"

        # Simulated route for testing
        self.simulated_route = [
            "Head north on Main Street for 200 meters",
            "Turn right onto College Road",
            "Walk straight for 300 meters",
            "Turn left at the traffic light",
            "Your destination is 50 meters ahead on your right",
            "You have arrived at your destination"
        ]

    def get_current_location(self):
        """Get current GPS location."""
        if self.simulation_mode:
            # GLA University, Mathura
            return 27.2090, 77.4977
        else:
            # Real GPS from gps_sos module
            from modules.gps_sos import GPSSOS
            gps = GPSSOS()
            return gps.get_gps_location()

    def get_route(self, start_lat, start_lon, end_lat, end_lon):
        """Get walking route from OpenRouteService API."""
        try:
            url = "https://api.openrouteservice.org/v2/directions/foot-walking"
            headers = {"Authorization": self.ORS_API_KEY}
            params = {
                "start": f"{start_lon},{start_lat}",
                "end": f"{end_lon},{end_lat}"
            }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            steps = []
            for segment in data['features'][0]['properties']['segments']:
                for step in segment['steps']:
                    steps.append(step['instruction'])
            return steps

        except Exception as e:
            print(f"[Navigation] ❌ Route error: {e}")
            return None

    def navigate_to(self, destination_name, dest_lat=None, dest_lon=None):
        """Start navigation to destination."""
        self.destination = destination_name
        self.current_step = 0
        self.is_navigating = True

        print(f"[Navigation] Starting navigation to: {destination_name}")
        self.tts.speak(f"Starting navigation to {destination_name}")

        if self.simulation_mode:
            route = self.simulated_route
        else:
            lat, lon = self.get_current_location()
            route = self.get_route(lat, lon, dest_lat, dest_lon)

        if not route:
            self.tts.speak("Could not find route. Please try again.")
            return

        # Navigate step by step
        thread = threading.Thread(target=self._navigate_steps, args=(route,))
        thread.daemon = True
        thread.start()

    def _navigate_steps(self, route):
        """Speak navigation steps one by one."""
        for i, step in enumerate(route):
            if not self.is_navigating:
                break

            self.current_step = i + 1
            print(f"[Navigation] Step {i+1}/{len(route)}: {step}")
            self.tts.speak(step)

            # Wait before next instruction
            time.sleep(8)

        if self.is_navigating:
            self.tts.speak("You have reached your destination!")
            self.is_navigating = False

    def stop_navigation(self):
        """Stop ongoing navigation."""
        self.is_navigating = False
        self.tts.speak("Navigation stopped.")
        print("[Navigation] Navigation stopped.")

    def get_status(self):
        """Get current navigation status."""
        return {
            'is_navigating': self.is_navigating,
            'destination': self.destination,
            'current_step': self.current_step
        }

    def run(self):
        """Test navigation."""
        print("[Navigation] Testing navigation system...")
        self.navigate_to("GLA University Main Gate")
        time.sleep(60)  # Let it run for 60 seconds


# Quick test
if __name__ == "__main__":
    nav = Navigation()
    nav.run()