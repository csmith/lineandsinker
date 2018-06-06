class Service:

    factories = []

    def accept_hook(self, identifier, request):
        pass

    @classmethod
    def add_factory(cls, factory):
        cls.factories.append(factory)
