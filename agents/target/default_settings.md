# Default Settings

| Field ID | Setting | Type | Required | Default | Guidance |
|---|---|---|---|---|---|
| `target_company` | Target Company | text | Yes | — | Include identifiers sufficient to distinguish the entity. |
| `buyer_company` | Buyer Company | text | Yes | — | Required for a named-buyer offer assessment; disclose if identity is confidential or unverified. |
| `research_cutoff_date` | Research Cut-off Date | date | Yes | — | Latest date up to which information may be considered. |
| `valuation_date` | Valuation Date | date | No | Research cut-off date | If omitted, the future runtime must use the research cut-off date. Disclose justified exceptions. |
| `report_language` | Report Language | text | No | English | Language for the final report. |
| `report_currency` | Report Currency | text | No | USD | Preserve source currencies and disclose conversions. |
| `deal_background` | What is the deal background? | longtext | No | Not specified | Describe the approach, transaction history, current status, and decision to be supported. |
| `offer_terms` | What are the offer terms? | longtext | No | Not specified | Provide consideration, value definition, payment mechanics, perimeter, conditions, and any amendments. |
| `shareholder_priorities` | What are shareholders' priorities? | longtext | No | Not specified | Identify evidenced priorities concerning value, liquidity, timing, control, risk, and retained upside. Distinguish differences among holders. |
| `available_financials_and_forecasts` | What financials and forecasts are available? | longtext | No | Not specified | Identify statements, forecasts, assumptions, periods, and their sources. Distinguish management forecasts from analyst scenarios. |
| `other_offers_and_discussions` | Are there other offers or ongoing discussions? | longtext | No | Not specified | Identify actual offers or discussions and their status. Separate these from hypothetical alternatives. |
| `shareholders_and_decision_makers` | Who are the key shareholders and decision-makers? | longtext | No | Not specified | Identify relevant holders, security classes, voting or approval rights, decision-makers, and known conflicts. |
| `approvals_and_deadlines` | What approvals and deadlines apply? | longtext | No | Not specified | Identify known approvals, response dates, contractual deadlines, and timing constraints. |
| `negotiation_priorities` | What are the negotiation priorities? | longtext | No | Not specified | Identify price, payment, liquidity, certainty, protections, or other priorities and explicit limits. |
| `available_documents_and_scope` | What documents are available, and what's in scope? | longtext | No | Not specified | List available documents and locations, access restrictions, included work, and exclusions. Listing a document does not establish runtime access. |
| `additional_context` | Additional Context | longtext | No | Not specified | Supplementary context and concerns. |

## Input handling contract

- Apply defaults before prompt construction. Resolve an omitted valuation date to the research cut-off date, not the run date.
- Preserve "Unknown" and "Not available" as supplied; do not silently replace them with facts or client preferences.
- All question-list fields must be inserted into this agent's prompt. A separate question-list document alone does not affect research.
- Listed documents require actual runtime access; this schema does not implement file upload.
- The manifest defines the reviewed content interface. Runtime validation and ATL registration remain to be implemented.
