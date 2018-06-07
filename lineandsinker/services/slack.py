import json

from .service import Service


class Slack(Service):
    def __init__(self):
        super().__init__("slack")

    def accept_hook(self, identifier, request):
        if request.content_type == "application/json":
            content = request.json()
        else:
            content = json.loads(request.get_data()["payload"])

        yield {"type": f"slack", "source": identifier, "text": content["text"]}
