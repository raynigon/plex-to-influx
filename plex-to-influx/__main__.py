"""
contains the PlexInfluxdbCollector and the main function
"""
import time
import logging
import argparse

from helpers import ConfigManager
from plex_input import PlexTvPlatform, PlexClient
from output.influxdb import PlexInfluxDBClient

class PlexInfluxdbCollector:

    def __init__(self, single_run=False):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.plex_client: PlexClient = None
        self.single_run = single_run
        config_manager = ConfigManager("config.ini")
        self.config = config_manager.config
        # InfluxDB
        self.influx_client = PlexInfluxDBClient(self.config)
        self.influx_client.connect()

        # Plex
        base_url = "{}://{}:32400".format(self.config.conn_security, self.config.plex_server_address)
        token = self.get_auth_token(self.config.plex_user, self.config.plex_password)
        self.plex_client = PlexClient(base_url, self.config.plex_hostname, token)

    def get_auth_token(self, username, password):
        plex_platform = PlexTvPlatform()
        return plex_platform.fetch_auth_token(username, password)

    def run(self):
        self.__log.info("Starting Monitoring Loop")
        delay = int(self.config.delay)
        while True:
            measurements = []
            measurements += self.plex_client.get_recently_added()
            measurements += self.plex_client.get_library_data()
            measurements += self.plex_client.get_active_streams()
            self.influx_client.write_points(measurements)
            if self.single_run:
                return
            time.sleep(delay)

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
