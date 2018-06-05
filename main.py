import hashlib

import jenkins
import requests
import os
from bs4 import BeautifulSoup
from flask import Flask

BASE_URL = os.environ["LAS_BASE_URL"]
SECRET = os.environ["LAS_SECRET"]

server = jenkins.Jenkins(
    os.environ["LAS_JENKINS_URL"],
    username=os.environ["LAS_JENKINS_USER"],
    password=os.environ["LAS_JENKINS_PASSWORD"],
)


def get_hook_url(service, identifier):
    nonce = (service + SECRET + identifier).encode("ascii")
    token = hashlib.sha256(nonce).hexdigest()
    return f"{BASE_URL}hooks/{service}/{identifier}/{token}"


def get_jenkins_jobs():
    for job in server.get_all_jobs():
        config = BeautifulSoup(server.get_job_config(job["fullname"]), features="xml")
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


app = Flask(__name__)


@app.route("/")
def handle_index():
    return app.send_static_file("index.html")


app.run('0.0.0.0')
