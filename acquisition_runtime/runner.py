"""Independent run records, input snapshots, and research execution."""
import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .output_handler import save_report, write_json
from .prompt_builder import build_prompt
from .settings import load_manifest, validate_settings


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_error(exc):
    text = str(exc)
    for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "X_SERVICE_TOKEN"):
        secret = os.getenv(name)
        if secret:
            text = text.replace(secret, "[redacted]")
    text = re.sub(r"sk-[A-Za-z0-9_-]+", "[redacted]", text)
    return text[:1000]


def run_agent(agent_root, settings, provider):
    return provider.run(build_prompt(agent_root, settings))


def execute_run(agent_root, submitted, provider=None, *, output_directory="output",
                dry_run=False, save_docx=True, save_pdf=False):
    root = Path(agent_root)
    settings = validate_settings(root, submitted)
    prompt = build_prompt(root, settings)
    if provider is None and not dry_run:
        raise ValueError("A research provider is required.")
    manifest = load_manifest(root)
    run_id = "run_" + uuid4().hex
    directory = Path(output_directory).resolve() / manifest["agent_id"] / run_id
    directory.mkdir(parents=True, exist_ok=False)
    record = {"run_id": run_id, "agent_id": manifest["agent_id"], "status": "prepared" if dry_run else "running",
              "created_at": utc_now(), "completed_at": None,
              "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
              "provider": getattr(provider, "provider_name", None),
              "model": getattr(provider, "model", None), "usage": None,
              "actual_cost_micro": None, "warnings": []}
    record_path = directory / "run.json"
    write_json(record_path, record)
    try:
        write_json(directory / "settings.json", settings)
        if dry_run:
            (directory / "prepared_prompt.md").write_text(prompt, encoding="utf-8")
            record["warnings"] = ["Preview only: no research request was sent and no report was generated."]
            write_json(record_path, record)
            return {"directory": str(directory), "record": record, "artifacts": {}}
        result = provider.run(prompt)
        artifacts = save_report(result, directory, save_docx=save_docx, save_pdf=save_pdf)
        record.update(status="completed", completed_at=utc_now(), provider=result.provider,
                      model=result.metadata.get("model", record["model"]),
                      usage=result.metadata.get("usage"),
                      actual_cost_micro=result.metadata.get("actual_cost_micro"),
                      warnings=artifacts["warnings"], artifacts=artifacts)
        write_json(record_path, record)
        return {"directory": str(directory), "record": record, "artifacts": artifacts}
    except BaseException as exc:
        record.update(status="failed", completed_at=utc_now(),
                      error="Research interrupted." if isinstance(exc, KeyboardInterrupt) else safe_error(exc))
        write_json(record_path, record)
        raise
