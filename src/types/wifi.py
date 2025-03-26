import geocoder
from geopy.distance import geodesic
import threading
import time

class WIFILocation:
    def __init__(self, manager):
        self.__wifi = geocoder.ip('me')
        print("WIFI connected.")
        self.__manager = manager

        # Start WIFI thread
        self.__running = True
        self.__thread = threading.Thread(target=self.__run, daemon=True)
        self.__thread.start()

    def __run(self):
        while self.__running:
            print("WIFI location is now running.")
            location = self.current_location()
            if location:
                lat, lon = location
                self.__manager.set_wifi_location(lat, lon)
            time.sleep(10)

    def current_location(self):
        lat, lon = self.__wifi.latlng
        return (lat, lon)
