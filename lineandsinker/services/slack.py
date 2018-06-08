import json

from .service import Service


class Slack(Service):
    def __init__(self):
        super().__init__("slack")

    def accept_hook(self, identifier, request):
        if request.content_type == "application/json":
            content = request.json
        else:
            content = json.loads(request.form["payload"])

        text = content["text"].strip()
        if "attachments" in content:
            text += " " + " ".join(
                filter(
                    lambda x: len(x) > 0,
                    (a["fallback"].strip() for a in content["attachments"]),
                )
            )

        yield {"type": f"slack", "source": identifier, "text": text}
