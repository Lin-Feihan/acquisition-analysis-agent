# Default Settings

| Field ID | Setting | Type | Required | Default | Guidance |
|---|---|---|---|---|---|
| `acquirer_company` | Acquirer Company | text | Yes | — | Include identifiers sufficient to distinguish the entity. |
| `target_company` | Target Company | text | Yes | — | Include identifiers sufficient to distinguish the entity. |
| `research_cutoff_date` | Research Cut-off Date | date | Yes | — | Latest date up to which information may be considered. |
| `valuation_date` | Valuation Date | date | No | Research cut-off date | If omitted, the future runtime must use the research cut-off date. Disclose justified exceptions. |
| `report_language` | Report Language | text | No | English | Language for the final report. |
| `report_currency` | Report Currency | text | No | USD | Preserve source currencies and disclose conversions. |
| `deal_background` | What is the deal background? | longtext | No | Not specified | Describe the opportunity, transaction history, current status, and decision to be supported. |
| `acquisition_objectives` | What are BuyCo's objectives? | longtext | No | Not specified | Describe the strategic, operating, or financial objectives and why acquisition is being considered. |
| `proposed_price_and_terms` | Are any price or terms proposed? | longtext | No | Not specified | Provide any proposed consideration, value definition, payment mechanics, perimeter, and material terms. State if no offer exists. |
| `funding_and_return_requirements` | What are the funding and return requirements? | longtext | No | Not specified | Provide any financing constraints, liquidity needs, capital-allocation priorities, or defined return requirements. |
| `available_financials_and_forecasts` | What financials and forecasts are available? | longtext | No | Not specified | Identify available statements, forecasts, assumptions, periods, and their sources. Distinguish management forecasts from analyst scenarios. |
| `integration_priorities` | What are the integration priorities? | longtext | No | Not specified | Describe integration objectives, priorities, constraints, retention concerns, and known dependencies. |
| `approvals_and_deadlines` | What approvals and deadlines apply? | longtext | No | Not specified | Identify known approvals, decision dates, contractual deadlines, and timing constraints. |
| `negotiation_priorities` | What are the negotiation priorities? | longtext | No | Not specified | Identify price, payment, protections, control, timing, or other priorities and any explicit limits. |
| `available_documents_and_scope` | What documents are available, and what's in scope? | longtext | No | Not specified | List available documents and locations, access restrictions, included work, and exclusions. Listing a document does not establish that the runtime can access it. |
| `additional_context` | Additional Context | longtext | No | Not specified | Supplementary context and concerns. |

## Input handling contract

- Apply defaults before prompt construction. Resolve an omitted valuation date to the research cut-off date, not the run date.
- Preserve "Unknown" and "Not available" as supplied; do not silently replace them with facts or client preferences.
- All question-list fields must be inserted into this agent's prompt. A separate question-list document alone does not affect research.
- Listed documents require actual runtime access; this schema does not implement file upload.
- The manifest defines the reviewed content interface. Runtime validation and ATL registration remain to be implemented.
