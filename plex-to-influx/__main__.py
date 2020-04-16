import time
import logging
import argparse
from typing import List

from helpers import ConfigManager
from plex_input import PlexTvPlatform, PlexClient, PlexMeasurement
from output.influxdb import PlexInfluxDBClient

class PlexInfluxdbCollector:

    def __init__(self, single_run=False):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.plex_clients: List[PlexClient] = []
        self.single_run = single_run
        config_manager = ConfigManager("config.ini")
        self.config = config_manager.config
        # InfluxDB
        self.influx_client = PlexInfluxDBClient(self.config)
        self.influx_client.connect()

        self._build_server_list()

    def _build_server_list(self):
        """
        Build a list of plexapi objects from the servers provided in the config
        :return:
        """
        for server in self.config.plex_server_addresses:
            base_url = "{}://{}:32400".format(self.config.conn_security, server)
            token = self.get_auth_token(self.config.plex_user, self.config.plex_password)
            self.plex_clients.append(PlexClient(base_url, server, token))

    def get_auth_token(self, username, password):
        plex_platform = PlexTvPlatform()
        return plex_platform.fetch_auth_token(username, password)

    def get_active_streams(self) -> List[PlexMeasurement]:
        measurements = []
        for client in self.plex_clients:
            measurements += client.get_active_streams()
        return measurements

    def get_library_data(self) -> List[PlexMeasurement]:
        measurements = []
        for client in self.plex_clients:
            measurements += client.get_library_data()
        return measurements

    def get_recently_added(self) -> List[PlexMeasurement]:
        measurements = []
        for client in self.plex_clients:
            measurements += client.get_recently_added()
        return measurements

    def run(self):
        self.__log.info("Starting Monitoring Loop")
        while True:
            measurements = []
            measurements += self.get_recently_added()
            measurements += self.get_library_data()
            measurements += self.get_active_streams()
            self.influx_client.write_points(measurements)
            if self.single_run:
                return
            time.sleep(self.config.delay)

def main():
    parser = argparse.ArgumentParser(
        description="A tool to send Plex statistics to InfluxDB")
    parser.add_argument("--singlerun", action="store_true",
                        help="Only runs through once, does not keep monitoring")
    args = parser.parse_args()
    collector = PlexInfluxdbCollector(single_run=args.singlerun)
    collector.run()

if __name__ == "__main__":
    main()
