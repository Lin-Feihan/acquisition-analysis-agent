# acquisition-analysis-agent

Deep research agents that help M&A analysts gather company information, conduct due diligence, perform valuation analyses, evaluate offers and deal terms, and compare alternatives to inform negotiation strategies from both the acquirer and target company perspectives.

## Two independent agents

| Agent | Agent ID | Content and runtime |
|---|---|---|
| Acquirer-Side Acquisition Analysis Agent | `acquirer-acquisition-analysis` | [agents/acquirer](agents/acquirer/README.md) |
| Target-Side Acquisition Offer Analysis Agent | `target-acquisition-analysis` | [agents/target](agents/target/README.md) |

Each agent has independent inputs, question list, prompt, report specification, and command. Shared code handles validation, provider transport, and output saving; there is no perspective-switch field.

## Status

The local runtime and offline checks are implemented. Live research calls, model availability, financial research quality, Word-based PDF conversion, and ATL registration are not yet verified. The nine research stages remain instructions to the research provider, not a separately implemented execution graph or certification system.

## Requirements

Python 3.12 or later. Run all commands from the repository root.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Optional document export dependencies:
python -m pip install -r requirements-export.txt
```

Dry runs and core offline tests need only the Python standard library. DOCX export needs python-docx. PDF export needs docx2pdf and Microsoft Word on a supported machine; its failure does not invalidate Markdown/evidence outputs.

## Preview without a research call

```powershell
python -m agents.acquirer.runtime.main --settings agents/acquirer/examples/hypothetical.json --dry-run
python -m agents.target.runtime.main --settings agents/target/examples/hypothetical.json --dry-run
```

The bundled examples are hypothetical inputs only. Preview output contains validated settings, a prepared prompt, and a run record with status `prepared`. It does not contain a research report or simulated evidence.

## Real research configuration

Use your own task settings and a service credential configured through your shell or secure deployment system. OPENAI_API_KEY may be omitted to enter it privately at the prompt. Do not put keys in task settings, code, screenshots, or Git commits. `.env.example` documents variable names; .env files are not loaded automatically.

- `OPENAI_API_KEY`: research-service API key.
- `OPENAI_BASE_URL`: optional ATL-supplied CommonStack OpenAI-compatible base URL. When set, synchronous gateway completion and `web_search` are used.
- `RESEARCH_MODEL`: required for a gateway; optional native-model override. Use a model supported by your service. Native config retains `o4-mini-deep-research` from the earlier agents; availability is not verified here.

Native OpenAI uses background Responses polling and the configured search tool. The runtime requests source metadata and preserves citations returned by the service. Unsupported tool/model combinations fail visibly; the code does not silently remove research tools and label the result equivalent.

Code Interpreter is off by default. A developer may enable `enable_code_interpreter` in the relevant agent's JSON-compatible `runtime/config.yaml` only when supported by the selected endpoint/model. Requesting a tool is not proof of its use. Inspect returned execution evidence. This version does not implement a standalone valuation calculator or XBRL checker.

The service timeout is configurable, as is the polling interval. On a polling wait-limit failure the runtime attempts cancellation; remote cancellation/billing cessation cannot be guaranteed. Interrupting a client likewise may leave a remote job running. No automatic retries create duplicate paid requests.

## Run independently

```powershell
python -m agents.acquirer.runtime.main --settings path/to/acquirer-settings.json
python -m agents.target.runtime.main --settings path/to/target-settings.json
```

Omit `--settings` to answer the corresponding agent's questions interactively. `--no-docx` skips DOCX; `--pdf` attempts PDF; `--output` selects a local output root.

All nine answers enter the corresponding research prompt. Missing optional answers retain explicit defaults; a missing valuation date uses the research cut-off date. Required fields, ISO dates, unknown keys, and template/schema mismatches are checked before research.

## Outputs

Each run receives a unique directory under `output/<agent-id>/<run-id>/`:

- `settings.json`: validated task inputs, without runtime credentials.
- `run.json`: agent ID, status, timestamps, prompt hash, returned model/usage, cost when actually returned, artifacts, and warnings.
- `report.md`: research-provider report, preserved without inventing references.
- `evidence.json`: returned citations, sources, and execution metadata; missing evidence remains missing.
- `report.docx` and `report.pdf`: optional exports.

Core report or evidence-save failures mark the run failed. Optional export failures preserve core outputs and add warnings. Missing structured citations/sources also produce warnings. Output and preview directories are ignored by Git and may contain sensitive client inputs; handle them accordingly.

## Checks

```powershell
python -m unittest discover -s tests -v
```

Checks use fake transports, not paid model calls. The DOCX check runs when its optional dependency is installed. See [validation scope](docs/runtime-validation.md).

## Next integration step

Register both IDs separately with atl-research-service, map each schema to its own ATL form, and adapt the existing run/result endpoints to these entry points. This repository does not yet change or deploy that service.
