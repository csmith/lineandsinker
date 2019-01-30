# Line and Sinker

![Hooks, lines and sinkers](static/las.jpg)

Line and Sinker (LaS) works with WebHooks from multiple services in order to
bridge them together. Think of it as a personal ifttt instance for development
and infrastructure tooling.

## Configuration

All configuration is done using environment variables to facilitate easy
deployment in a docker container.

Global settings:

Environment variable | Description
-------------------- | --------------------------------------------------------
 `LAS_BASE_URL`      | Base web-facing URL at which LaS is accessible, used to generate hook URLs
 `LAS_SECRET`        | Random string used to generate secure hook URLs
 `LAS_ADMIN_PASSWORD`| Password to require for web-based admin functionality

### URL format

LaS accepts WebHook calls to URLs in the format of
`/hook/<service>/<identifier>/<hash>`, where `<service>` is the service calling
(e.g. GitHub, Jenkins), `<identifier>` is some service-specific identifier for
the hook (e.g. the name of a repository or project), and `<hash>` is a
hex-encoded sha-256 hash of the service, LaS secret, and identifier
concatenated together. The secret prevents anyone that discovers the endpoint
from triggering hooks spuriously or maliciously.

## Supported services

### Docker registry

LaS accepts hooks from the docker registry. There are no configuration options.

### Gitea

Environment variable | Description
-------------------- | --------------------------------------------------------
 `LAS_GITEA_URL`     | Base URL of the Gitea instance to connect to
 `LAS_GITEA_TOKEN`   | Application token to use to authenticate to Gitea
 `LAS_GITEA_ADD_HOOKS` | If present, automatically add hooks to all repos

LaS accepts Gitea webhooks and can automatically add itself as a hook
for all repositories it has access to using the given token.

### Jenkins

Environment variable | Description
-------------------- | --------------------------------------------------------
 `LAS_JENKINS_URL`   | Base URL of the Jenkins instance to connect to
 `LAS_JENKINS_USER`  | Username of the Jenkins account to use to connect
 `LAS_JENKINS_PASSWORD` | Password of the Jenkins account to use

LaS accepts Jenkins webhooks but does not automatically create them. It can
start Jenkins jobs in response to other events.

### ReportBot

Environment variable | Description
-------------------- | --------------------------------------------------------
 `LAS_REPORTBOT_URL` | The full URL to the report API endpoint
 `LAS_REPORTBOT_KEY` | The authentication key to use
 `LAS_REPORTBOT_CHANNEL` | The channel to send messages to

LaS can send messages to a ReportBot instance.

### Sensu

LaS accepts JSON events from Sensu. There are no configuration options.

### Slack

LaS accepts Slack-style webhooks. There are no configuration options.

## Contributing

All code is formatted using [Black](https://github.com/ambv/black) with
default settings. There is a [pre-commit](https://pre-commit.com/)
config file to enable automatic black formatting on commit; to enable
it simply:

    pip install pre-commit
    pre-commit install
