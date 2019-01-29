from flask import Flask, abort, request

from lineandsinker.common import get_hook_key
from lineandsinker.services import services


def refresh_services():
    for service in services.values():
        service.refresh()


refresh_services()
app = Flask(__name__)


def handle_events(events):
    for event in events:
        if event["type"] == "git.push":
            services["jenkins"].build_job_by_scm_url(event["repo"]["urls"])
            if event["repo"]["public"]:
                services["irccat"].announce(
                    f"\002[git]\002 {event['user']} pushed {len(event['commits'])} commit{'s' if len(event['commits']) != 1 else ''} to {event['repo']['name']}: {event['compare_url']}"
                )

                for commit in event["commits"][::-1][:3]:
                    line = commit["message"].split("\n")[0][:100]
                    services["irccat"].announce(f"\002[git]\002 {commit['id']}: {line}")
        elif event["type"] == "docker.push":
            services["irccat"].announce(
                f"\002[registry]\002 New manifest pushed to {event['host']}/{event['repo']}:{event['tag']} by {event['user']}"
            )
        elif event["type"] == "slack":
            services["irccat"].announce(f"\002[{event['source']}]\002 {event['text']}")


@app.route("/")
def handle_index():
    return app.send_static_file("index.html")


@app.route("/hooks/<service>/<path:identifier>/<hash>", methods=["GET", "POST"])
def handle_hook(service, identifier, hash):
    app.logger.info(f"Received hook for {service} with identifier {hash}")

    expected_hash = get_hook_key(service, identifier)
    if hash != expected_hash:
        app.logger.info(f"Hash not valid. Expected: {expected_hash}, got {hash}")
        abort(403)

    if service not in services:
        app.logger.info(f"Unknown service {service}, known: {services.keys()}")
        abort(404)

    handle_events(services[service].accept_hook(identifier, request) or [])

    return "", 200


if __name__ == "__main__":
    app.run("0.0.0.0")
