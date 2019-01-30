from .service import Service


class Sensu(Service):
    def __init__(self):
        super().__init__("sensu")

    def accept_hook(self, identifier, request):
        yield {"type": "sensu", **request.get_json(force=True)}
