import requests

from .service import Service


class IrcCat(Service):
    def __init__(self, url, channel):
        super().__init__("irccat")
        self._url = url
        self._channel = channel

    def announce(self, message):
        for line in message.split("\n"):
            requests.post(
                self._url,
                f"{self._channel}, {line}",
            )
