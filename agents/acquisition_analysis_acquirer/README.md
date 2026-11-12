# Acquisition Analysis (Acquirer Side)

Supports the acquirer's management and board in assessing standalone value, synergies, financing, acquisition returns, risks, and offer strategy.

Agent ID: `acquisition-analysis-acquirer`

## Run

From the repository root:

```powershell
python -m agents.acquisition_analysis_acquirer.runtime.main
```

Or pass task settings:

```powershell
python -m agents.acquisition_analysis_acquirer.runtime.main --settings path/to/settings.json
```

For a preview without an API request:

```powershell
python -m agents.acquisition_analysis_acquirer.runtime.main --settings agents/acquisition_analysis_acquirer/examples/hypothetical.json --dry-run
```

## Files

- `question_list.md`: nine pre-research questions.
- `default_settings.md`: input definitions and defaults.
- `manifest.json`: agent metadata and input schema.
- `prompt.md`: research role, planning, nine stages, and reporting standards.
- `output_spec.md`: report structure.
- `runtime/`: execution entry points and configuration.
- `examples/hypothetical.json`: configuration example for preview.

Outputs are saved under `output/acquisition-analysis-acquirer/<run-id>/`. See the [root README](../../README.md) for installation, service configuration, exports, and validation status.
