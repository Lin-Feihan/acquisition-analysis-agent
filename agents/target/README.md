# Target-Side Acquisition Offer Analysis Agent

This agent has its own ID, question list, input schema, research prompt, report specification, and execution entry point. It does not switch perspectives.

## Run from the repository root

Preview the complete task without credentials or a research request:

```powershell
python -m agents.target.runtime.main --settings agents/target/examples/hypothetical.json --dry-run
```

For real research, install the root requirements, configure credentials, and provide your own task settings:

```powershell
python -m agents.target.runtime.main --settings path/to/your-settings.json
```

Omit `--settings` to answer the input questions interactively. See the [repository instructions](../../README.md) for service configuration and exports.

## Files

- `question_list.md`: nine questions corresponding to this agent's workflow diagram.
- `default_settings.md`: inputs, defaults, and missing-information behavior.
- `manifest.json`: independent agent ID and platform input schema.
- `prompt.md`: role, client mandate, research planning, nine stages, and reporting standards.
- `output_spec.md`: independent report structure.
- `runtime/`: this agent's entry point and adapters to shared infrastructure.
- `examples/hypothetical.json`: input-only preview example; not a real transaction or completed research.

## Outputs and limits

Each run saves to `output/target-acquisition-analysis/run_<unique-id>/`. Real completed runs save `report.md`, `evidence.json`, `settings.json`, and `run.json`. DOCX export is optional and PDF additionally requires Word and docx2pdf. Export failures produce warnings while core outputs remain available.

No live research quality, complete nine-stage execution, XBRL verification, independent certification, or ATL integration is claimed. The runtime invokes one research request using this agent's approved workflow; it does not implement a separate nine-node graph. Listed documents are not automatically uploaded or read.
