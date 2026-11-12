# Acquisition Analysis (Target Company Side)

Supports the target company's board in assessing an offer against standalone value and alternatives, including payment quality, shareholder proceeds, liquidity, and deal certainty.

Agent ID: `acquisition-analysis-target-company`

## Run

From the repository root:

```powershell
python -m agents.acquisition_analysis_target_company.runtime.main
```

Or pass task settings:

```powershell
python -m agents.acquisition_analysis_target_company.runtime.main --settings path/to/settings.json
```

For a preview without an API request:

```powershell
python -m agents.acquisition_analysis_target_company.runtime.main --settings agents/acquisition_analysis_target_company/examples/hypothetical.json --dry-run
```

## Files

- `question_list.md`: nine pre-research questions.
- `default_settings.md`: input definitions and defaults.
- `manifest.json`: agent metadata and input schema.
- `prompt.md`: research role, planning, nine stages, and reporting standards.
- `output_spec.md`: report structure.
- `runtime/`: execution entry points and configuration.
- `examples/hypothetical.json`: configuration example for preview.

Outputs are saved under `output/acquisition-analysis-target-company/<run-id>/`. See the [root README](../../README.md) for installation, service configuration, exports, and validation status.
