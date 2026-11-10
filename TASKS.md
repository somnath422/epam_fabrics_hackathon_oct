# Team task board

Updated: November 10, 2026. This is the shared source of truth for progress. Update task status only when the stated evidence exists; do not mark a planned item complete because it appears in a diagram or pitch. Keep one task at a time with the user-facing builder, and capture screenshots/exports for cloud-only work.

## Status key

- **DONE** — implementation and evidence verified.
- **PARTIAL** — a useful portion works; acceptance below is not yet met.
- **READY** — next actionable task; not started.
- **BLOCKED** — requires an external permission, artifact, or decision; record the blocker.

## Verified progress

| Workstream | Status | Verified evidence |
|---|---|---|
| Synthetic source and Lakehouse Bronze/Silver/Gold foundation | **DONE** | 6,669,117 source rows; seven Silver entity tables, two Gold foundation tables, validation checks documented in `PROJECT_MEMORY.md`. Synthetic-data limitations remain. |
| Churn model and held-out evaluation | **DONE** | Saved Spark logistic-regression pipeline; account/time-disjoint test; metrics and signed contributions documented in `PROJECT_MEMORY.md`. Fabric ML registry registration is still open. |
| Power BI portfolio, account history, and tasks | **DONE** | Three pages; September 30, 2025 coverage/risk counts verified. Direct Lake mode and Purview labels remain unverified. |
| Historical risk-score replay to Eventhouse | **DONE** | Seven saved synthetic risk-score events observed. This is not a raw behavioral-event stream or live inference. |
| Activator to durable review task | **DONE** | Event-level rule invoked the validating notebook; task was created and visible. Notification was not attempted. |
| Fabric Ontology Preview | **DONE** | Six OneLake-bound entity types, five Account relationships, composite keys, descriptions, instance previews, and sample Ontology Agent queries. |
| Ontology source export | **DONE** | Cleaned RDF/XML at [`ontology.rdf`](./ontology.rdf), commit `0f78750`; removed unbound `cancel_date` and `subscription_status`, corrected synonym to “Engagement Snapshot.” Preview status and re-importability still need validation. |
| Judges' material and project handoff | **DONE** | Editable deck, corrected demo script, capability review, architecture and memory are in `submission/` and repository root. |

## Remaining work, in dependency order

| ID | Task | Owner(s) | Status | Depends on | Acceptance evidence |
|---|---|---|---|---|---|
| T01 | Build KQL account journey and three behavioral signals | Sujith + Ashish | **DONE** | Existing Eventhouse connection; choose bounded historical account cohort | Verified 121-row replay for ACC008178 in separate `customer_usage_observations_demo`; KQL returns 30 days per comparison window, matching Spark reference averages and three declines; saved `usage_journey_001_degradation`. Historical replay disclosed; existing risk-event/Activator path untouched. |
| T02 | Define canonical identity rules and match-quality report | Ashish + Archi | **DONE** | Existing generated IDs; use a small explicitly synthetic multi-source match sample if testing resolution | Tenant-scoped exact-key-only auto-match rule documented; synthetic fixture exercised duplicates, missing keys, unmatched and ambiguous domains; 2 TP / 0 FP / 3 FN (100% precision, 40% recall); cross-tenant case remained unmatched. This measures only the fixture, not real-world identity quality. |
| T03 | Add versioned behavioral segmentation and membership history | Irfan + Archi | **READY** | T01 signal definitions | Distinct behavioral segment vs. risk band; rule version, as-of date, evidence and run ID persisted; repeat run creates no duplicates; previous membership remains auditable. |
| T04 | Register the existing model and persist complete metrics | Irfan | **READY** | Confirm Fabric ML registry support; preserve active release | Registered version reloads successfully; scores match existing pipeline; metric definitions/denominators include accuracy, precision, recall, lift, F1 and PR-AUC; signed attribution reconstruction still passes. |
| T05 | Confirm Direct Lake mode and apply available Purview labels | Lokesh + Somnath | **READY** | Inspect current semantic model and tenant governance capabilities | Capture actual storage mode; label inventory covers personal/contact-like fields and documents unsupported surfaces; test access with approved identities. Do not claim unavailable controls. |
| T06 | Approve a risk-based retention marketing playbook | Archi | **READY** | Supported signals/segments from T01/T03 | Small approved strategy set with eligibility, evidence, audience/channel, consent/suppression, owner/approver and success measure. No generic discount assumption or automatic outreach. |
| T07 | Build grounded agent-assisted retention brief | Somnath + Sujith + Archi | **READY** | T01, T03, T04, T06; verify Copilot Studio access first | Supported account query and cited brief use approved read-only data/playbooks; unauthorized/missing/stale evidence is denied or abstained; CSM/Marketing approval required; task and notification states are distinct. |
| T08 | Export cloud implementation and run end-to-end acceptance | Somnath + all owners | **READY** | Each workstream's exports | Sanitized notebooks/configs/metrics/report/KQL/ontology evidence in approved repo; positive, duplicate, stale, unauthorized, failure and retry paths checked; no credentials committed. |
| T09 | Rehearse and submit the 5–10-minute judge demo | Archi + Somnath | **READY** | T08 and organizers' confirmed submission instructions | One timed rehearsal, backup recording/screenshots, consistent labels and counts; clearly distinguishes synthetic historical proof from future capabilities. |

## Current next action: T03, add versioned behavioral segmentation and membership history

T01 is complete. The user created and saved a bounded synthetic historical usage replay in `customer_usage_observations_demo`, verified its 121 rows / 121 unique events for one account from June 2 through September 30, 2025, and saved the KQL comparison query `usage_journey_001_degradation`. KQL and Spark use inclusive windows of Aug 2-31 and Sep 1-30, with 30 observations each. The observed averages match: active users 12.6667 to 6.4, API calls 1900.1333 to 951.3667, and seat utilization 30.89% to 15.61%; declines are approximately 49.47%, 49.93%, and 49.47%, respectively.

The usage observations are a synthetic historical replay, not live inference or production telemetry. The new table is separate; do not alter `customer_risk_events`, its Eventstream route, or Activator source. The cloud notebook/query have not been exported to Git.

T02 is complete using the source profile and synthetic fixture executed in `09_identity_match_quality_demo`. Silver profile: 10,000 account rows and 10,000 contact rows; unique `(tenant_id, account_id)` on both; zero orphan contact account keys; zero `account_id` reuse across tenants; zero duplicate non-empty domains within a tenant; and one contact row per account. The contact source has no email, so no email-based identity claim is made.

Canonical rule: auto-match only when both `tenant_id` and `account_id` are present and their exact pair resolves to exactly one catalog row. Duplicate exact keys, missing tenant, missing account, and domain-only evidence are not automatically linked; domain candidates are only review suggestions scoped to a supplied tenant, and ambiguous domains require review. Never match across tenants. On the separate eight-record synthetic fixture, results were TP=2, FP=0, FN=3 (100% precision, 40% recall); duplicate-key, missing-tenant, domain-candidate, ambiguous-domain, and unmatched cases were observed, and a cross-tenant lookalike remained unmatched. These metrics characterize only the deliberately constructed fixture, not production or multi-source match quality. Notebook evidence remains cloud-only.

## Team update protocol

After each user-visible milestone:

1. Record the task ID, status, date, owner, evidence location, and limitation in this file.
2. Update `PROJECT_MEMORY.md` if a durable architecture, data, or operational fact changed.
3. Keep secrets and raw private customer payloads out of Git.
4. Commit/push the board and related safe evidence so teammates share the same state.
