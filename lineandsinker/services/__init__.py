import os

from .docker import Docker
from .gitea import Gitea
from .jenkins import Jenkins
from .reportbot import ReportBot


def docker_factory():
    return Docker()


def gitea_factory():
    return Gitea(os.environ["LAS_GITEA_URL"], os.environ["LAS_GITEA_TOKEN"])


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


services = {
    "docker": docker_factory(),
    "gitea": gitea_factory(),
    "jenkins": jenkins_factory(),
    "reportbot": reportbot_factory(),
}
