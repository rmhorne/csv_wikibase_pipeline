#executor_factory.py
from executors.dry import DryExecutor
from executors.simulate import SimulateExecutor
from executors.commit import CommitExecutor

EXECUTORS = {
    "dry": DryExecutor,
    "simulate": SimulateExecutor,
    "commit": CommitExecutor,
}


def get_executor(mode):
    try:
        return EXECUTORS[mode]()
    except KeyError:
        raise ValueError(f"Unknown mode: {mode}")
