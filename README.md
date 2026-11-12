# acquisition-analysis-agent
Deep research agents that help M&amp;A analysts gather company information, conduct due diligence, perform valuation analyses, evaluate offers and deal terms, and compare alternatives to inform negotiation strategies from both the acquirer and target company perspectives.

## Two independent agents

| Agent | Agent ID | Content package |
|---|---|---|
| Acquirer-Side Acquisition Analysis Agent | `acquirer-acquisition-analysis` | [agents/acquirer](agents/acquirer/README.md) |
| Target-Side Acquisition Offer Analysis Agent | `target-acquisition-analysis` | [agents/target](agents/target/README.md) |

Each agent has its own question list, input schema, research prompt, and output specification. Neither uses a perspective-switch input.

## Status

Reviewed content specifications only. Runtime development, provider/tool integration, export implementation, and ATL registration remain pending. Research prompts are task instructions, not proof that a nine-stage execution graph, feedback loop, calculation service, or independent verification system has been implemented.

The content follows the user-reviewed acquirer-side and target-side prompts. Fixed case information is parameterized; case claims must be verified or explicitly labeled as hypothetical.

## Package structure

Each directory contains `README.md`, `agent_card.md`, `question_list.md`, `default_settings.md`, `manifest.json`, `prompt.md`, and `output_spec.md`.

Question-list answers enter the prompt through matching task variables. The future runtime must apply defaults, set an omitted valuation date to the research cut-off date, inject the relevant output specification, and validate inputs before starting research.

The reporting standards are embedded in each independent prompt. Document availability fields describe inputs; they do not implement file upload or grant access to private documents.
