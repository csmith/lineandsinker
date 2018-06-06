import re
from functools import wraps

from flask import Flask, abort, request, Response

from lineandsinker.common import get_hook_key
from lineandsinker.services import services

url_pattern = re.compile(
    "^/hooks/(?P<service>[^/]+)/(?P<identifier>.*)/(?P<key>[^/]+)$"
)


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        path = request.path
        match = url_pattern.match(path)

        if not match:
            return Response("Bad request", 400)

        expected_key = get_hook_key(match.group("service"), match.group("identifier"))
        if expected_key != match.group("key"):
            app.logger.info(f"Bad request to {path}: expected key {expected_key}")
            return Response("Invalid key", 403)

        return f(*args, **kwargs)

    return wrapper


repos = dict((name, [ssh, clone]) for name, ssh, clone in services["gitea"].get_repos())
jobs = list(services["jenkins"].get_jobs())
app = Flask(__name__)


@app.route("/")
def handle_index():
    return app.send_static_file("index.html")


@app.route("/hooks/gitea/<path:repo>/<hash>", methods=["POST"])
@authenticate
def handle_hook_gitea(repo):
    app.logger.info(f"Received hook for repo {repo}")

    if repo not in repos:
        app.logger.info(f"Repository not found. Known repos: {repos.keys()}")
        abort(404)

    if request.headers.get("X-Gitea-Event") == "push":
        urls = repos[repo]
        for name, spec, url in jobs:
            if url in urls:
                # TODO: Check branches
                app.logger.info(f"Found matching job: {name} with URL {url}")
                services["jenkins"].build_job(name)

        data = request.get_json()
        if not data["repository"]["private"]:
            repo = data["repository"]["full_name"]
            commits = len(data["commits"])
            compare = data["compare_url"]
            pusher = data["pusher"]["login"]

            services["reportbot"].announce(
                f"\002[git]\002 {pusher} pushed {commits} commit{'s' if commits != 1 else ''} to {repo}: {compare}"
            )
            for commit in data["commits"][:3]:
                services["reportbot"].announce(
                    f"\002[git]\002 {commit['id'][:10]}: {commit['message'][:100]}"
                )

    return "", 204


@app.route("/hooks/docker/registry/<hash>", methods=["GET", "POST"])
@authenticate
def handle_docker_registry():
    for event in request.get_json()["events"]:
        if (
            event["action"] == "push"
            and "vnd.docker.distribution.manifest" in event["target"]["mediaType"]
            and "tag" in event["target"]
        ):
            repo = event["target"]["repository"]
            tag = event["target"]["tag"]
            host = event["request"]["host"]
            user = event["actor"]["name"]
            services["reportbot"].announce(
                f"\002[registry]\002 New manifest pushed to {host}/{repo}:{tag} by {user}"
            )

    return "", 204


if __name__ == "__main__":
    app.run("0.0.0.0")
