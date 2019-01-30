import os

from collections import deque
from flask import Flask, abort, request, Response, render_template
from functools import wraps

from lineandsinker.common import get_hook_key
from lineandsinker.services import services


def refresh_services():
    for service in services.values():
        service.refresh()


refresh_services()
history = deque(maxlen=100)
app = Flask(__name__)


def handle_events(events):
    for event in events:
        history.append(event)
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
        elif event["type"] == "sensu":
            state = event["check"]["state"].upper()
            if state == "FAILING":
                state = f"\0034{state}\003"
            services["irccat"].announce(
                f"`{event['check']['metadata']['name']}` is now \002{state}\002\n{event['check']['output']}",
                "#sensu",
            )


@app.route("/")
def handle_index():
    return render_template("index.html")


@app.route("/hooks/<service>/<path:identifier>/<hash>", methods=["GET", "POST"])
def handle_hook(service, identifier, hash):
    app.logger.info(f"Received hook for {service} with identifier {hash}")

    expected_hash = get_hook_key(service, identifier)
    if hash != expected_hash:
        handle_events(
            [
                {
                    "type": "lineandsinker.badhash",
                    "service": service,
                    "hash": hash,
                    "body": request.get_data(as_text=True),
                }
            ]
        )
        app.logger.info(f"Hash not valid. Expected: {expected_hash}, got {hash}")
        abort(403)

    if service not in services:
        handle_events(
            [
                {
                    "type": "lineandsinker.badservice",
                    "service": service,
                    "known_services": list(services.keys()),
                    "body": request.get_data(as_text=True),
                }
            ]
        )
        app.logger.info(f"Unknown service {service}, known: {services.keys()}")
        abort(404)

    handle_events(services[service].accept_hook(identifier, request) or [])

    return "", 200


if "LAS_ADMIN_PASSWORD" in os.environ:

    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if (
                not auth
                or auth.username != "admin"
                or auth.password != os.environ["LAS_ADMIN_PASSWORD"]
            ):
                return Response(
                    "Restricted resource",
                    401,
                    {"WWW-Authenticate": 'Basic realm="Login Required"'},
                )
            return f(*args, **kwargs)

        return decorated

    @app.route("/admin")
    @requires_auth
    def handle_admin():
        return render_template("admin.html", events=history)

    @app.route("/admin/hash", methods=["POST"])
    @requires_auth
    def handle_admin_hash():
        return get_hook_key(request.form["service"], request.form["identifier"]), 200


if __name__ == "__main__":
    app.run("0.0.0.0")
