from src.types.wifi import WIFILocation
from src.types.gps import GPSLocation


class LocationManager():
    def __init__(self):
        self.__gps = GPSLocation(self)
        self.__gps_latest_location = None
        self.__wifi = WIFILocation(self)
        self.__wifi_latest_location = None

    def set_gps_location(self, location):
        self.__gps_latest_location = location

    def set_wifi_location(self, location):
        self.__wifi_latest_location = location

    def current_location(self):
        if self.__gps.can_get_location():
            return (self.__gps.__get_location())
        elif self.__wifi.can_get_location():
            return (self.__wifi.current_location())

    def close(self):
        self.__gps.close()
