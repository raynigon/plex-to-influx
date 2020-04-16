"""
plex_measurement contains a data class to store all informations needed for a single measurement
"""

class PlexMeasurement:

    def __init__(self, name, host):
        self.name = name
        self.fields = {}
        self.__tags = {
            "host": host
        }

    def append_tag(self, key: str, value: str):
        if key == "host":
            raise Exception("Overwriting host tag is not allowed")
        self.__tags[key] = value

    def to_influx_dict(self):
        return {
            "measurement": self.name,
            "fields": self.fields,
            "tags": self.__tags
        }
