from pathlib import Path
from acquisition_runtime.runner import run_agent as _run

AGENT_ROOT = Path(__file__).resolve().parents[1]


def run_agent(settings, provider):
    return _run(AGENT_ROOT, settings, provider)
