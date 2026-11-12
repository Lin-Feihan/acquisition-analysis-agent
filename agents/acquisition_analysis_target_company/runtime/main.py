"""Run with: python -m agents.acquisition_analysis_target_company.runtime.main"""
from pathlib import Path
from acquisition_runtime.cli import main as run_cli

AGENT_ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    return run_cli(AGENT_ROOT, argv)


if __name__ == "__main__":
    raise SystemExit(main())
