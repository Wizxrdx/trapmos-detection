from src.types.wifi import WIFILocation
from src.types.gps import GPSLocation


class LocationManager():
    def __init__(self):
        self.__gps = GPSLocation(self)
        self.__gps_latest_location = None
        self.__wifi = WIFILocation(self)
        self.__wifi_latest_location = None

    def set_gps_location(self, lat, lon):
        self.__gps_latest_location = (lat, lon)

    def set_wifi_location(self, lat, lon):
        self.__wifi_latest_location = (lat, lon)

    def current_location(self):
        if self.__gps_latest_location is not None:
            return self.__gps_latest_location
        elif self.__wifi_latest_location is not None:
            return self.__wifi_latest_location
        else:
            return (0, 0)

    def close(self):
        self.__gps.close()
