import os

from .jenkins import Jenkins
from .gitea import Gitea
from .reportbot import ReportBot


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


factories = {"gitea": gitea_factory, "jenkins": jenkins_factory}
