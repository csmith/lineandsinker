import os

from jsonref import requests

from ..common import get_hook_url
from .service import Service


class Gitea(Service):
    def __init__(self, url, token, install_hooks=False):
        self._url = url
        self._token = token
        self._install_hooks = install_hooks

    def get_repos(self):
        repos = self._request("get", f"user/repos").json()
        for repo in repos:
            if self._install_hooks:
                self._maybe_install_gitea_hook(repo["full_name"])
            yield repo["full_name"], repo["ssh_url"], repo["clone_url"]

    def _maybe_install_gitea_hook(self, project):
        hook_url = get_hook_url("gitea", project)
        path = f"repos/{project}/hooks"
        hooks = self._request("get", path).json()

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
            self._request("post", path, json=body).json()

    def _request(self, method, api_path, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["access_token"] = self._token
        return requests.request(method, f"{self._url}api/v1/{api_path}", **kwargs)


def gitea_factory():
    return Gitea(os.environ["LAS_GITEA_URL"], os.environ["LAS_GITEA_TOKEN"])


Service.add_factory(gitea_factory)
