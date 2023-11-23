import copy

from kubespider_source_provider import Manager

manager = Manager()


@manager
class TestProvider:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @manager.search
    def search(self):
        data = copy.deepcopy(self.kwargs)
        data['search'] = True
        return data

    @manager.schedule
    def schedule(self):
        data = copy.deepcopy(self.kwargs)
        data['schedule'] = True
        return data


if __name__ == '__main__':
    manager.run()
