"""One-pass substitution: inserted user text is never treated as a template."""
import re
from pathlib import Path

from .settings import validate_settings

VARIABLE = re.compile(r"\{\{([^{}]+)\}\}")


def build_prompt(agent_root, settings):
    root = Path(agent_root)
    settings = validate_settings(root, settings)
    template = (root / "prompt.md").read_text(encoding="utf-8")
    output_spec = (root / "output_spec.md").read_text(encoding="utf-8")
    if not output_spec.strip():
        raise ValueError("Output specification is empty.")
    values = {**settings, "output_specification": output_spec}
    variables = set(VARIABLE.findall(template))
    missing = variables - values.keys()
    unused = settings.keys() - variables
    if missing or unused:
        raise ValueError(f"Template/schema mismatch: missing={sorted(missing)}, unused={sorted(unused)}")
    return VARIABLE.sub(lambda match: str(values[match.group(1)]), template)
