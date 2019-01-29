import os

from .docker import Docker
from .gitea import Gitea
from .irccat import IrcCat
from .jenkins import Jenkins
from .reportbot import ReportBot
from .slack import Slack

services = {}

try:
    services["docker"] = Docker()
except:
    pass

try:
    services["gitea"] = Gitea(
        os.environ["LAS_GITEA_URL"],
        os.environ["LAS_GITEA_TOKEN"],
        install_hooks="LAS_GITEA_ADD_HOOKS" in os.environ,
    )
except:
    pass

try:
    services["irccat"] = IrcCat(
        os.environ["LAS_IRCCAT_HOST"],
        int(os.environ["LAS_IRCCAT_PORT"]),
        os.environ["LAS_IRCCAT_CHANNEL"],
    )
except:
    pass

try:
    services["jenkins"] = Jenkins(
        os.environ["LAS_JENKINS_URL"],
        os.environ["LAS_JENKINS_USER"],
        os.environ["LAS_JENKINS_PASSWORD"],
    )
except:
    pass

try:
    services["reportbot"] = ReportBot(
        os.environ["LAS_REPORTBOT_URL"],
        os.environ["LAS_REPORTBOT_KEY"],
        os.environ["LAS_REPORTBOT_CHANNEL"],
    )
except:
    pass

try:
    services["slack"] = Slack()
except:
    pass
