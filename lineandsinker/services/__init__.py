import os

from .docker import Docker
from .gitea import Gitea
from .irccat import IrcCat
from .jenkins import Jenkins
from .reportbot import ReportBot
from .slack import Slack


def docker_factory():
    return Docker()


def gitea_factory():
    return Gitea(
        os.environ["LAS_GITEA_URL"],
        os.environ["LAS_GITEA_TOKEN"],
        install_hooks="LAS_GITEA_ADD_HOOKS" in os.environ,
    )

def irccat_factory():
    return IrcCat(
        os.environ["LAS_IRCCAT_HOST"],
        int(os.environ["LAS_IRCCAT_PORT"]),
        os.environ["LAS_IRCCAT_CHANNEL"],
    )

def jenkins_factory():
    return Jenkins(
        os.environ["LAS_JENKINS_URL"],
        os.environ["LAS_JENKINS_USER"],
        os.environ["LAS_JENKINS_PASSWORD"],
    )


def reportbot_factory():
    return ReportBot(
        os.environ["LAS_REPORTBOT_URL"],
        os.environ["LAS_REPORTBOT_KEY"],
        os.environ["LAS_REPORTBOT_CHANNEL"],
    )


def slack_factory():
    return Slack()


services = {
    "docker": docker_factory(),
    "gitea": gitea_factory(),
    "irccat": irccat_factory(),
    "jenkins": jenkins_factory(),
    "reportbot": reportbot_factory(),
    "slack": slack_factory(),
}
