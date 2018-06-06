import os

from .jenkins import Jenkins
from .gitea import Gitea


def gitea_factory():
    return Gitea(os.environ["LAS_GITEA_URL"], os.environ["LAS_GITEA_TOKEN"])


def jenkins_factory():
    return Jenkins(
        os.environ["LAS_JENKINS_URL"],
        os.environ["LAS_JENKINS_USER"],
        os.environ["LAS_JENKINS_PASSWORD"],
    )


factories = {"gitea": gitea_factory, "jenkins": jenkins_factory}
