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
| T01 | Build KQL account journey and three behavioral signals | Sujith + Ashish | **READY — next** | Existing Eventhouse connection; choose bounded historical account cohort | Saved KQL queries derive usage decline, API decline and adoption deterioration from longitudinal observations; cross-check selected account/dates against Spark; disclose historical replay. Do not modify the working risk-event/Activator path. |
| T02 | Define canonical identity rules and match-quality report | Ashish + Archi | **READY** | Existing generated IDs; use a small explicitly synthetic multi-source match sample if testing resolution | Written deterministic tenant-scoped rules; known duplicate, unmatched and ambiguous cases; precision/recall against separate synthetic ground truth; no silent cross-tenant merges. |
| T03 | Add versioned behavioral segmentation and membership history | Irfan + Archi | **READY** | T01 signal definitions | Distinct behavioral segment vs. risk band; rule version, as-of date, evidence and run ID persisted; repeat run creates no duplicates; previous membership remains auditable. |
| T04 | Register the existing model and persist complete metrics | Irfan | **READY** | Confirm Fabric ML registry support; preserve active release | Registered version reloads successfully; scores match existing pipeline; metric definitions/denominators include accuracy, precision, recall, lift, F1 and PR-AUC; signed attribution reconstruction still passes. |
| T05 | Confirm Direct Lake mode and apply available Purview labels | Lokesh + Somnath | **READY** | Inspect current semantic model and tenant governance capabilities | Capture actual storage mode; label inventory covers personal/contact-like fields and documents unsupported surfaces; test access with approved identities. Do not claim unavailable controls. |
| T06 | Approve a risk-based retention marketing playbook | Archi | **READY** | Supported signals/segments from T01/T03 | Small approved strategy set with eligibility, evidence, audience/channel, consent/suppression, owner/approver and success measure. No generic discount assumption or automatic outreach. |
| T07 | Build grounded agent-assisted retention brief | Somnath + Sujith + Archi | **READY** | T01, T03, T04, T06; verify Copilot Studio access first | Supported account query and cited brief use approved read-only data/playbooks; unauthorized/missing/stale evidence is denied or abstained; CSM/Marketing approval required; task and notification states are distinct. |
| T08 | Export cloud implementation and run end-to-end acceptance | Somnath + all owners | **READY** | Each workstream's exports | Sanitized notebooks/configs/metrics/report/KQL/ontology evidence in approved repo; positive, duplicate, stale, unauthorized, failure and retry paths checked; no credentials committed. |
| T09 | Rehearse and submit the 5–10-minute judge demo | Archi + Somnath | **READY** | T08 and organizers' confirmed submission instructions | One timed rehearsal, backup recording/screenshots, consistent labels and counts; clearly distinguishes synthetic historical proof from future capabilities. |

## Current next action: T01, one step at a time

Start with read-only verification; do not send new events or edit the existing Activator source.

1. In Fabric, open the existing **Eventhouse** `eh_customer_intelligence`.
2. Open the KQL database `eh_customer_intelligence`.
3. Open the table `customer_risk_events` and run:

   ```kusto
   customer_risk_events
   | take 5
   ```

4. Confirm whether those rows contain actual usage observations (active users, sessions, API calls) or only saved risk-score events.
5. Capture the column names or a screenshot and report back before creating any query.

**Expected from the existing setup:** `customer_risk_events` contains risk-score events, not daily source usage observations. If so, stop here; the next action is to prepare a small bounded usage-observation export from `silver_usage_daily` and ingest it to a separate Eventhouse table. Do not calculate usage-behavior journeys from risk-score events or label scores as usage behavior.

## Team update protocol

After each user-visible milestone:

1. Record the task ID, status, date, owner, evidence location, and limitation in this file.
2. Update `PROJECT_MEMORY.md` if a durable architecture, data, or operational fact changed.
3. Keep secrets and raw private customer payloads out of Git.
4. Commit/push the board and related safe evidence so teammates share the same state.
