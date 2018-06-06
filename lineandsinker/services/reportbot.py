import requests

from .service import Service


class ReportBot(Service):
    def __init__(self, url, key, channel):
        super().__init__("reportbot")
        self._url = url
        self._key = key
        self._channel = channel

    def announce(self, message):
        requests.get(
            self._url,
            {"key": self._key, "command": f"CM {self._channel}", "args": message},
        )
