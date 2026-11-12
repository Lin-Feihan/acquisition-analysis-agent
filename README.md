# acquisition-analysis-agent

Deep research agents that help M&A analysts gather company information, conduct due diligence, perform valuation analyses, evaluate offers and deal terms, and compare alternatives to inform negotiation strategies from both the acquirer and target company perspectives.

## Agents

| Agent | Agent ID | Directory |
|---|---|---|
| Acquisition Analysis (Acquirer Side) | `acquisition-analysis-acquirer` | [agents/acquisition_analysis_acquirer](agents/acquisition_analysis_acquirer/README.md) |
| Acquisition Analysis (Target Company Side) | `acquisition-analysis-target-company` | [agents/acquisition_analysis_target_company](agents/acquisition_analysis_target_company/README.md) |

Each agent has its own inputs, question list, prompt, report specification, and entry point. Common runtime code is in `acquisition_runtime/`.

## Installation

Python 3.12 or later. Run commands from the repository root.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Optional document exports:
python -m pip install -r requirements-export.txt
```

DOCX requires python-docx. PDF additionally requires docx2pdf and Microsoft Word. Failed optional exports preserve the report and evidence.

## Configuration

Set credentials in the environment, or enter the API key privately when prompted.

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Research-service API key |
| `OPENAI_BASE_URL` | Optional CommonStack-compatible service URL |
| `RESEARCH_MODEL` | Required gateway model; optional native-model override |

`.env.example` lists the variables; .env files are not loaded automatically. Keep real keys out of source files and task settings.

Each agent's `runtime/config.yaml` contains JSON-compatible YAML. Preserve that syntax when editing. Native OpenAI uses background polling; the gateway path expects synchronous completion. The native default is `o4-mini-deep-research`; configure a model and tools supported by your service. Code Interpreter is disabled by default.

## Run

```powershell
python -m agents.acquisition_analysis_acquirer.runtime.main
python -m agents.acquisition_analysis_target_company.runtime.main
```

Each command collects the corresponding agent's inputs. To read settings from a JSON file:

```powershell
python -m agents.acquisition_analysis_acquirer.runtime.main --settings path/to/acquirer-settings.json
python -m agents.acquisition_analysis_target_company.runtime.main --settings path/to/target-settings.json
```

Use `--dry-run` to validate inputs and save the assembled prompt without an API request. Configuration examples:

```powershell
python -m agents.acquisition_analysis_acquirer.runtime.main --settings agents/acquisition_analysis_acquirer/examples/hypothetical.json --dry-run
python -m agents.acquisition_analysis_target_company.runtime.main --settings agents/acquisition_analysis_target_company/examples/hypothetical.json --dry-run
```

Other options: `--output` selects an output root, `--no-docx` skips DOCX, and `--pdf` attempts PDF export.

All nine question-list answers enter the research prompt. Missing optional answers retain their defaults; an omitted valuation date uses the research cut-off date. Listed documents are not automatically uploaded.

## Outputs

Each run saves under `output/<agent-id>/<run-id>/`:

- `settings.json`: validated inputs.
- `run.json`: status, timestamps, model, returned usage/cost, artifacts, and warnings.
- `report.md`: research report.
- `evidence.json`: returned citations, sources, and tool metadata.
- `report.docx` and `report.pdf`: optional exports.

A dry run saves `prepared_prompt.md` instead of a report. Output directories are excluded from Git. Core output failures mark a run failed; export failures and missing structured evidence produce warnings.

## Tests and status

```powershell
python -m unittest discover -s tests -v
```

The 17 local checks passed using simulated research services; the DOCX check requires its optional dependency. Live API compatibility, research quality, Word-based PDF conversion, and ATL deployment remain unverified.

The nine-stage workflows are research instructions to the provider. This version does not implement a separate workflow graph or XBRL verification service. On a wait-limit failure the runtime attempts cancellation; a remote task may continue after timeout or interruption.
