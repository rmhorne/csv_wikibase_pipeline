from .base import BaseExecutor

from output import write_plan_json


class DryExecutor(BaseExecutor):
    def process(self, plan):
        write_plan_json(plan)
        print("✔ plan_output.json written")
