import location.wifi as wifi
import location.gps as gps


class LocationManager():
    def __init__(self):
        self.gps = gps.connect_gps()
        self.wifi = wifi.connect_wifi()

    def current_location(self):
        if self.gps.can_get_location():
            return self.gps.current_location()
        elif self.wifi.can_get_location():
            return self.wifi.current_location()

    def close(self):
        self.gps.close()
