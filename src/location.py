from src.types.wifi import WIFILocation
from src.types.gps import GPSLocation


class LocationManager():
    def __init__(self):
        self.gps = GPSLocation()
        self.wifi = WIFILocation()

    def current_location(self):
        if self.gps.can_get_location():
            return self.gps.current_location()
        elif self.wifi.can_get_location():
            return self.wifi.current_location()

    def close(self):
        self.gps.close()
