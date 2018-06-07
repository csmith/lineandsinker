from .service import Service


class Docker(Service):
    def __init__(self):
        super().__init__("docker")

    def accept_hook(self, identifier, request):
        for event in request.get_json()["events"]:
            if (
                event["action"] == "push"
                and "vnd.docker.distribution.manifest" in event["target"]["mediaType"]
                and "tag" in event["target"]
            ):
                yield {
                    "type": "docker.push",
                    "repo": event["target"]["repository"],
                    "tag": event["target"]["tag"],
                    "host": event["request"]["host"],
                    "user": event["actor"]["name"],
                }
