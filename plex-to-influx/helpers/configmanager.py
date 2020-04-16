"""
configmanager contains the config model and the ConfigurationManager class
"""

import os
import logging
import configparser

ENV_PROPERTY_MAPPING = {
    "PDC_GENERAL_DELAY": "delay",
    "PDC_GENERAL_REPORTCOMBINED": "report_combined",

    "PDC_INFLUXDB_ADDRESS": "influx_address",
    "PDC_INFLUXDB_PORT": "influx_port",
    "PDC_INFLUXDB_DATABASE": "influx_database",
    "PDC_INFLUXDB_SSL": "influx_ssl",
    "PDC_INFLUXDB_VERIFYSSL": "influx_verify_ssl",
    "PDC_INFLUXDB_USERNAME": "influx_user",
    "PDC_INFLUXDB_PASSWORD": "influx_password",

    "PDC_PLEX_SERVERS": "plex_server_addresses",
    "PDC_PLEX_USERNAME": "plex_user",
    "PDC_PLEX_PASSWORD": "plex_password",
    "PDC_PLEX_HTTPS": "plex_https",
    "PDC_PLEX_VERIFYSSL": "plex_verify_ssl",

    "PDC_LOGGING_LEVEL": "logging_level",
}


class Config:

    def __init__(self):
        # General
        self.delay = 5
        self.report_combined = True

        # InfluxDB
        self.influx_address = None
        self.influx_port = 8086
        self.influx_database = "plex_data"
        self.influx_ssl = False
        self.influx_verify_ssl = False
        self.influx_user = ""
        self.influx_password = ""

        # Plex
        self.plex_user = None
        self.plex_password = None
        self.plex_https = False
        self.conn_security = "http"
        self.plex_verify_ssl = False
        self.plex_server_addresses = []

        #Logging
        self.logging_level = "critical"


class ConfigManager:

    def __init__(self, config):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__log.info("Loading config: %s", config)
        self.config = Config()
        self.__configfile = configparser.ConfigParser()

        config_file = os.path.join(os.getcwd(), config)
        if os.path.isfile(config_file):
            self.__configfile.read(config_file)

        self._load_config_values()
        self.__log.info("Configuration Successfully Loaded")

    def _load_config_values(self):

        # General
        self.config.delay = self.__configfile["GENERAL"].getint("Delay", fallback=2)
        self.config.report_combined = self.__configfile["GENERAL"].get("ReportCombined", fallback=True)

        # InfluxDB
        self.config.influx_address = self.__configfile["INFLUXDB"]["Address"]
        self.config.influx_port = self.__configfile["INFLUXDB"].getint("Port", fallback=8086)
        self.config.influx_database = self.__configfile["INFLUXDB"].get("Database", fallback="plex_data")
        self.config.influx_ssl = self.__configfile["INFLUXDB"].getboolean("SSL", fallback=False)
        self.config.influx_verify_ssl = self.__configfile["INFLUXDB"].getboolean("Verify_SSL", fallback=True)
        self.config.influx_user = self.__configfile["INFLUXDB"].get("Username", fallback="")
        self.config.influx_password = self.__configfile["INFLUXDB"].get("Password", fallback="", raw=True)

        # Plex
        self.config.plex_user = self.__configfile["PLEX"]["Username"]
        self.config.plex_password = self.__configfile["PLEX"].get("Password", raw=True)
        self.config.plex_https = self.__configfile["PLEX"].getboolean("HTTPS", fallback=False)
        self.config.plex_verify_ssl = self.__configfile["PLEX"].getboolean("Verify_SSL", fallback=False)
        self.config.plex_server_addresses = self.__configfile["PLEX"]["Servers"]

        #Logging
        self.config.logging_level = self.__configfile["LOGGING"].get("Level", fallback="critical")

        ## Overwrite Properties
        for key, value in ENV_PROPERTY_MAPPING.items():
            if key not in os.environ.keys():
                continue
            setattr(self.config, value, os.environ[key])

        if self.config.plex_server_addresses == "":
            raise Exception("Missing Plex Server Addresses")
        self.config.plex_server_addresses = self.config.plex_server_addresses.replace(" ", "").split(",")
        self.config.conn_security = "https" if self.config.plex_https else "http"
        self.config.logging_level = self.config.logging_level.upper()
