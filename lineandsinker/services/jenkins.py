import jenkins
from bs4 import BeautifulSoup

from .service import Service


class Jenkins(Service):

    SCM_CLASS = "hudson.plugins.git.GitSCM"

    def __init__(self, url, username, password):
        super().__init__("jenkins")
        self._server = jenkins.Jenkins(url, username=username, password=password)

    def get_jobs(self):
        for job in self._server.get_all_jobs():
            name = job["fullname"]
            config = BeautifulSoup(self._server.get_job_config(name), features="xml")
            for git_config in config.find_all("scm", class_=self.SCM_CLASS):
                branch_spec = git_config.find("branches").find("name").text
                yield name, branch_spec, git_config.find("url").text

    def build_job(self, name):
        self._server.build_job(name)
