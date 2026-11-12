# Target-Side Acquisition Offer Analysis Agent

This is an independent agent content package. It has its own ID, input schema, question list, research prompt, and output specification.

## Contents

- `question_list.md`: the nine pre-research questions from the corresponding workflow diagram.
- `default_settings.md`: field definitions, defaults, and missing-input behavior.
- `manifest.json`: machine-readable registration and input specification.
- `prompt.md`: role, injected mandate, planning, nine research stages, and embedded reporting standards.
- `output_spec.md`: the independent report structure.

## Planned execution

Collect and validate settings → inject settings and output specification → invoke a research provider → save the report and available evidence.

## Current status

Content only. No runtime, tool integration, XBRL verification, calculation module, or ATL registration is claimed. Output format declarations describe intended support, not generated artifacts. DOCX/PDF export can be added when implemented.
