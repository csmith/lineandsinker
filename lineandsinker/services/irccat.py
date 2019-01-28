import socket

from .service import Service


class IrcCat(Service):
    def __init__(self, host, port, channel):
        super().__init__("irccat")
        self._host = host
        self._port = port
        self._channel = channel

    def announce(self, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._host, self._port))
        for line in message.split("\n"):
            s.sendall(bf"{self._channel} {line}\n")
        s.close()
