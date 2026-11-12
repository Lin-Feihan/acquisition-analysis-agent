from pathlib import Path
from acquisition_runtime.prompt_builder import build_prompt as _build

AGENT_ROOT = Path(__file__).resolve().parents[1]


def build_prompt(settings):
    return _build(AGENT_ROOT, settings)
