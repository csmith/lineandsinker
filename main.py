import hashlib

import jenkins
import requests
import os
from bs4 import BeautifulSoup
from flask import Flask, abort

BASE_URL = os.environ["LAS_BASE_URL"]
SECRET = os.environ["LAS_SECRET"]

jenkins_server = jenkins.Jenkins(
    os.environ["LAS_JENKINS_URL"],
    username=os.environ["LAS_JENKINS_USER"],
    password=os.environ["LAS_JENKINS_PASSWORD"],
)


def get_hook_key(service, identifier):
    nonce = (service + SECRET + identifier).encode("ascii")
    return hashlib.sha256(nonce).hexdigest()


def get_hook_url(service, identifier):
    return f"{BASE_URL}hooks/{service}/{identifier}/{get_hook_key(service, identifier)}"


def get_jenkins_jobs():
    for job in jenkins_server.get_all_jobs():
        config = BeautifulSoup(
            jenkins_server.get_job_config(job["fullname"]), features="xml"
        )
        for git_config in config.find_all("scm", class_="hudson.plugins.git.GitSCM"):
            branch_spec = git_config.find("branches").find("name").text
            yield job["fullname"], branch_spec, git_config.find("url").text


def maybe_install_gitea_hook(project):
    gitea_url = f"{os.environ['LAS_GITEA_URL']}api/v1/repos/{project}/hooks"
    hook_url = get_hook_url("gitea", project)
    hooks = requests.get(
        gitea_url, params={"access_token": os.environ["LAS_GITEA_TOKEN"]}
    ).json()

    if hook_url not in [hook["config"]["url"] for hook in hooks]:
        body = {
            "active": True,
            "config": {"content_type": "json", "url": hook_url},
            "events": [
                "create",
                "delete",
                "fork",
                "push",
                "issues",
                "issue_comment",
                "pull_request",
                "repository",
                "release",
            ],
            "type": "gitea",
        }
        requests.post(
            gitea_url,
            json=body,
            params={"access_token": "5b8de94a7201bc923e99813850327caf75b85e70"},
        ).json()


def get_gitea_repos():
    repos = requests.get(
        f"{os.environ['LAS_GITEA_URL']}api/v1/user/repos",
        params={"access_token": os.environ["LAS_GITEA_TOKEN"]},
    ).json()
    for repo in repos:
        maybe_install_gitea_hook(repo["full_name"])
        yield repo["full_name"], repo["ssh_url"], repo["clone_url"]


repos = dict((name, [ssh, clone]) for name, ssh, clone in get_gitea_repos())
jobs = list(get_jenkins_jobs())
app = Flask(__name__)


@app.route("/")
def handle_index():
    return app.send_static_file("index.html")


@app.route("/hooks/gitea/<path:repo>/<hash>")
def handle_hook_gitea(repo, hash):
    print(f"Received hook for repo {repo} with has {hash}")
    expected_hash = get_hook_key("gitea", repo)
    if hash != expected_hash:
        print(f"Hash mismatch: expected {expected_hash}")
        abort(403)

    if repo not in repos:
        print(f"Repository not found. Known repos: {repos.keys()}")
        abort(404)

    urls = repos[repo]
    for name, spec, url in jobs:
        if url in urls:
            # TODO: Check branches
            print(f"Found matching job: {name} with URL {url}")
            jenkins_server.build_job(name)

    return "", 204


app.run("0.0.0.0")
