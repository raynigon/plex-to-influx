"""
plex_client contains the logic to connect to the PlexServer
for which the metrics should be collected
"""

import logging
import time
from typing import List

import requests
from plexapi.server import PlexServer

from .plex_measurement import PlexMeasurement


class PlexClient:

    def __init__(self, url, host, token):
        # Init Logger
        self.__log = logging.getLogger(self.__class__.__name__)

        # Init Client API
        session = requests.Session()  # TODO handle: session.verify = config.plex_verify_ssl
        self.__connection = PlexServer(url, token, session=session)
        self.__host = host

        # Init Data Attributes
        self.__active_streams = {}

    def get_recently_added(self) -> List[PlexMeasurement]:
        measurements = []
        recent_list = []
        for section in self.__connection.library.sections():
            recent_list += section.recentlyAdded(maxresults=10)
        for item in recent_list:
            title = item.title
            media_type = item.type.title()
            added_at = item.addedAt.strftime("%Y-%m-%dT%H:%M:%SZ")
            if hasattr(item, "grandparentTitle"):
                title = f"{item.grandparentTitle} - {item.title}"
            # Create Measurement
            measurement = PlexMeasurement("recently_added", self.__host)
            measurement.fields = {
                "title": title,
                "media_type": media_type,
                "added_at": added_at,
            }
            measurements.append(measurement)
        return measurements

    def get_library_data(self) -> List[PlexMeasurement]:
        measurements = []
        libs = self.__connection.library.sections()
        for library in libs:
            measurement = PlexMeasurement("libraries", self.__host)
            measurement.append_tag("type", library.type)
            measurement.fields = {
                "title": library.title,
                "item_count": len(library.search()),
            }
            if library.type == "show":
                seasons = 0
                episodes = 0
                shows = library.search()
                for show in shows:
                    seasons += len(show.seasons())
                    episodes += len(show.episodes())
                measurement.fields["season_count"] = seasons
                measurement.fields["episode_count"] = episodes
            measurements.append(measurement)
        return measurements

    def get_active_streams(self) -> List[PlexMeasurement]:
        measurements = []
        self.__log.debug("Attempting to get active sessions")
        active_streams = self.__connection.sessions()
        active_streams = filter(lambda stream: len(stream.session) > 0, active_streams)
        self.__log.debug("Processing Active Streams")

        for stream in active_streams:
            player = stream.players[0]
            user = stream.usernames[0]
            session_id = stream.session[0].id
            transcode = stream.transcodeSessions if stream.transcodeSessions else None
            if session_id in self.__active_streams:
                start_time = self.__active_streams[session_id]["start_time"]
            else:
                start_time = time.time()
                self.__active_streams[session_id] = {}
                self.__active_streams[session_id]["start_time"] = start_time
            media_type = stream.type
            # Build the title. TV and Music Have a root title plus episode/track name.  Movies don"t
            if hasattr(stream, "grandparentTitle"):
                full_title = stream.grandparentTitle + " - " + stream.title
            else:
                full_title = stream.title
            if media_type != "track":
                resolution = stream.media[0].videoResolution
            else:
                resolution = str(stream.media[0].bitrate) + "Kbps"
            measurement = PlexMeasurement("now_playing", self.__host)
            measurement.append_tag("player_address", player.address)
            measurement.append_tag("session_id", session_id)
            measurement.fields = {
                "stream_title": full_title,
                "player": player.title,
                "state": player.state,
                "user": user,
                "resolution": resolution,
                "media_type": media_type,
                "playback": "transcode" if transcode else "direct",
                "duration": time.time() - start_time,
            }
            measurements.append(measurement)
        current_streams = map(lambda stream: stream.session[0].id, active_streams)
        remove_keys = []
        for session_id, _ in self.__active_streams.items():
            if session_id not in current_streams:
                remove_keys.append(session_id)
        for key in remove_keys:
            self.__active_streams.pop(key)

        return measurements

    def _remove_dead_streams(self, current_streams):
        """
        Go through the stored list of active streams and remove any that are no longer active
        :param current_streams: List of currently active streams from last API call
        :return:
        """
        remove_keys = []
        for key, _ in self.__active_streams.items():
            if key not in current_streams:
                remove_keys.append(key)
        for key in remove_keys:
            self.__active_streams.pop(key)
