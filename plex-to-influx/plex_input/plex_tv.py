"""
plex_tv contains the interface to the plex.tv rest api
"""
import logging
import requests

PLEX_PLATFORM_CLIENT_HEADERS = {
    "X-Plex-Client-Identifier": "Plex InfluxDB Collector",
    "X-Plex-Product": "Plex InfluxDB Collector",
    "X-Plex-Version": "1",
}
PLEX_PLATFORM_USER_INFO_URL = "https://plex.tv/users/sign_in.json"


class PlexTvPlatform:

    def __init__(self):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__token = None

    def fetch_auth_token(self, username: str, password: str) -> str:
        """
        Make a reqest to plex.tv to get an authentication token for future requests
        :param username: Plex Username
        :param password: Plex Password
        :return: str
        """

        self.__log.info(f"Getting Auth Token For User: {username}")

        response = requests.post(PLEX_PLATFORM_USER_INFO_URL,
                                 auth=(username, password),
                                 headers=PLEX_PLATFORM_CLIENT_HEADERS)
        if response.status_code > 299:
            self.__log.error("Failed To Get Authentication Token")
            if response.status_code != 401:
                raise Exception("Failed To Get Authentication Token", response)
            self.__log.error(
                "Failed to get token due to bad username/password")
            return None
        output = response.json()

        # Make sure we actually got a token back
        if "user" not in output or "authToken" not in output["user"]:
            raise Exception("AuthToken is missing in the user object")
        self.__log.debug("Successfully Retrieved Auth Token")
        self.__token = output["user"]["authToken"]
        return self.__token
