from flask import Request


class Service:
    def __init__(self, type):
        self.type = type

    def refresh(self):
        pass

    def accept_hook(self, identifier, request: Request):
        pass
