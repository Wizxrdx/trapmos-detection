import geocoder
from geopy.distance import geodesic

class WIFILocation:
    def __init__(self):
        self.__wifi = geocoder.ip('me')
        print("WIFI connected.")

    def can_get_location(self):
        return self.__wifi.ok

    def current_location(self):
        if self.can_get_location():
            lat, lon = self.__wifi.latlng
            return (lat, lon)
        return (None, None)
