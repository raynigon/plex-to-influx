"""
influxdb contains the PlexInfluxDBClient
"""
import logging
from typing import List

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from requests import ConnectTimeout

from plex_input import PlexMeasurement


class PlexInfluxDBClient:

    def __init__(self, config):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.__influx = None


    def connect(self):
        """
        Create an InfluxDB connection and test to make sure it works.
        We test with the get all users command.  If the address is bad it fails
        with a 404.  If the user doesn"t have permission it fails with 401
        :return:
        """
        self.__influx = InfluxDBClient(
            self.config.influx_address,
            self.config.influx_port,
            database=self.config.influx_database,
            ssl=self.config.influx_ssl,
            verify_ssl=self.config.influx_verify_ssl,
            username=self.config.influx_user,
            password=self.config.influx_password,
            timeout=5
        )
        try:
            self.__log.debug("Testing connection to InfluxDb using provided credentials")
            self.__influx.ping()
            self.__log.debug("Successful connection to InfluxDb")
        except (ConnectTimeout, InfluxDBClientError) as exception:
            if isinstance(exception, ConnectTimeout):
                self.__log.critical(
                    "Unable to connect to InfluxDB at the provided address (%s)",
                    self.config.influx_address)
            elif exception.code == 401:
                self.__log.critical(
                    "Unable to connect to InfluxDB with provided credentials")
            raise exception

    def write_points(self, measurements: List[PlexMeasurement]):
        """
        Writes the provided JSON to the database
        :param json_data:
        :return:
        """
        points = map(PlexMeasurement.to_influx_dict, measurements)
        try:
            self.__influx.write_points(points)
        except (InfluxDBClientError, ConnectionError, InfluxDBServerError) as exception:
            self.__log.error("Failed to write data to InfluxDB, Exception: %s", exception)
        self.__log.debug("Written To Influx: %s", measurements)
