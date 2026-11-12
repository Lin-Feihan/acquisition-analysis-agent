# Local runtime validation

This document records software checks, not financial research results.

## Checked

- Independent prompts, report specifications, IDs, and output directories.
- Nine question-list responses enter each prompt.
- Required fields, date formats, unknown fields, and explicit missing answers.
- Valuation-date fallback to the research cut-off date.
- One-pass substitution; user text containing braces is not reinterpreted as template syntax.
- Dry runs do not call a provider or create a research report.
- Completed test runs save report, evidence, settings, and run records.
- Research/evidence failures produce failed records; optional export failures preserve core outputs.
- Native background polling, synchronous gateway handling, failed/incomplete/empty responses, and wait-limit cancellation attempts using simulated transports.
- Actual citation/source normalization, missing cost preservation, and tool-output retention without storing reasoning summaries.
- DOCX export has an optional content-preservation check when python-docx is installed.

## Not checked by these tests

No paid research request, provider/model availability, actual gateway compatibility, research accuracy, complete nine-stage performance, PDF conversion through Microsoft Word, or ATL integration has been verified. The bundled examples are hypothetical input examples, not completed case studies.

## Reproduce

From the repository root:

```powershell
python -m unittest discover -s tests -v
```

If the system temporary directory is unavailable, set TEMP and TMP to a writable directory before starting Python. Tests use local fake transports and never use research credentials.

## Source compatibility

The implementation follows the existing agent interface (settings → prompt → provider → report/evidence) and adapts the native/gateway distinction in atl-research-service. It currently implements OpenAI Responses and an OpenAI-compatible synchronous CommonStack path. Other providers from the older agents are not included yet.

Official API references:

- https://developers.openai.com/api/docs/guides/background
- https://developers.openai.com/api/docs/guides/tools-web-search
- https://developers.openai.com/api/docs/guides/tools-code-interpreter

Code Interpreter is disabled by default. Enabling it requests the tool but does not guarantee that the selected model/service supports or uses it. Retain and inspect returned tool evidence.
