from .service import Service


class Docker(Service):
    def __init__(self):
        super().__init__("docker")
