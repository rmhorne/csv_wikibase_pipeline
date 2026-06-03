from .base import BaseExecutor


class CommitExecutor(BaseExecutor):
    def setup(self):
        raise NotImplementedError("Commit mode is not implemented yet.")

    def process(self, plan):
        raise NotImplementedError("Commit mode is not implemented yet.")
