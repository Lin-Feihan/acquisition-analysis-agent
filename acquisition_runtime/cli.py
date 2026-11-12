"""CLI plumbing shared by two separate agent entry points."""
import argparse
import getpass
import json
import os
from pathlib import Path

from .providers import get_provider
from .runner import execute_run, safe_error
from .settings import collect_settings, validate_settings


def main(agent_root, argv=None):
    parser = argparse.ArgumentParser(description="Run this independent acquisition research agent.")
    parser.add_argument("--settings", type=Path, help="UTF-8 JSON task settings; otherwise prompt interactively.")
    parser.add_argument("--dry-run", action="store_true", help="Prepare the prompt without credentials or an API request.")
    parser.add_argument("--output", default="output", help="Local output directory.")
    parser.add_argument("--no-docx", action="store_true", help="Skip optional DOCX export.")
    parser.add_argument("--pdf", action="store_true", help="Attempt Word-based PDF export (optional dependencies required).")
    args = parser.parse_args(argv)
    try:
        root = Path(agent_root)
        if args.settings:
            settings = validate_settings(root, json.loads(args.settings.read_text(encoding="utf-8-sig")))
        else:
            settings = collect_settings(root)
        # JSON is a valid YAML subset; this deliberately needs no YAML parser.
        config = json.loads((root / "runtime" / "config.yaml").read_text(encoding="utf-8"))
        provider = None
        if not args.dry_run:
            gateway = bool(os.getenv("OPENAI_BASE_URL", "").strip())
            provider_config = config["providers"]["commonstack" if gateway else "openai"]
            if gateway and not os.getenv("RESEARCH_MODEL", "").strip():
                raise ValueError("Set RESEARCH_MODEL to the model supported by your gateway before running.")
            api_key = os.getenv("OPENAI_API_KEY", "").strip() or getpass.getpass("Research API key: ")
            provider = get_provider("commonstack" if gateway else "openai", api_key, provider_config)
        outcome = execute_run(root, settings, provider, output_directory=args.output,
                              dry_run=args.dry_run, save_docx=not args.no_docx, save_pdf=args.pdf)
        print("Prepared preview (no research call)." if args.dry_run else "Research completed.")
        print("Saved to: " + outcome["directory"])
        for warning in outcome["record"]["warnings"]:
            print("Warning: " + warning)
        return 0
    except KeyboardInterrupt:
        print("Interrupted. Any remote task may continue; check its service status.")
        return 130
    except Exception as exc:
        print("Run failed: " + safe_error(exc))
        return 1
