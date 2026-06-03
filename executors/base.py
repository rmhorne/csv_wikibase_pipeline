class BaseExecutor:
    def setup(self):
        pass

    def process(self, plan):
        raise NotImplementedError
