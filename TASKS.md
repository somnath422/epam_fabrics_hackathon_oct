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
| T01 | Build KQL account journey and three behavioral signals | Sujith + Ashish | **IN PROGRESS** | Existing Eventhouse connection; choose bounded historical account cohort | Saved KQL queries derive usage decline, API decline and adoption deterioration from longitudinal observations; cross-check selected account/dates against Spark; disclose historical replay. Do not modify the working risk-event/Activator path. |
| T02 | Define canonical identity rules and match-quality report | Ashish + Archi | **READY** | Existing generated IDs; use a small explicitly synthetic multi-source match sample if testing resolution | Written deterministic tenant-scoped rules; known duplicate, unmatched and ambiguous cases; precision/recall against separate synthetic ground truth; no silent cross-tenant merges. |
| T03 | Add versioned behavioral segmentation and membership history | Irfan + Archi | **READY** | T01 signal definitions | Distinct behavioral segment vs. risk band; rule version, as-of date, evidence and run ID persisted; repeat run creates no duplicates; previous membership remains auditable. |
| T04 | Register the existing model and persist complete metrics | Irfan | **READY** | Confirm Fabric ML registry support; preserve active release | Registered version reloads successfully; scores match existing pipeline; metric definitions/denominators include accuracy, precision, recall, lift, F1 and PR-AUC; signed attribution reconstruction still passes. |
| T05 | Confirm Direct Lake mode and apply available Purview labels | Lokesh + Somnath | **READY** | Inspect current semantic model and tenant governance capabilities | Capture actual storage mode; label inventory covers personal/contact-like fields and documents unsupported surfaces; test access with approved identities. Do not claim unavailable controls. |
| T06 | Approve a risk-based retention marketing playbook | Archi | **READY** | Supported signals/segments from T01/T03 | Small approved strategy set with eligibility, evidence, audience/channel, consent/suppression, owner/approver and success measure. No generic discount assumption or automatic outreach. |
| T07 | Build grounded agent-assisted retention brief | Somnath + Sujith + Archi | **READY** | T01, T03, T04, T06; verify Copilot Studio access first | Supported account query and cited brief use approved read-only data/playbooks; unauthorized/missing/stale evidence is denied or abstained; CSM/Marketing approval required; task and notification states are distinct. |
| T08 | Export cloud implementation and run end-to-end acceptance | Somnath + all owners | **READY** | Each workstream's exports | Sanitized notebooks/configs/metrics/report/KQL/ontology evidence in approved repo; positive, duplicate, stale, unauthorized, failure and retry paths checked; no credentials committed. |
| T09 | Rehearse and submit the 5–10-minute judge demo | Archi + Somnath | **READY** | T08 and organizers' confirmed submission instructions | One timed rehearsal, backup recording/screenshots, consistent labels and counts; clearly distinguishes synthetic historical proof from future capabilities. |

## Current next action: T01.2, calculate Spark reference signals

**Completed T01 verification:** the user ran a `take 5` query against `customer_risk_events`. Its rows are the historical risk-score replay, not the raw daily usage observations required for behavior signals.

**Completed T01.1 bounded preview:** the user created notebook `08_prepare_usage_journey_demo`, attached `lh_customer_intelligence`, and displayed **121 rows** for `ACC008178` / `TEN008178`, June 2 through September 30, 2025. The preview includes active users, sessions, API calls and licensed seats.

Before ingesting or creating Eventhouse queries, compute an independently inspectable Spark reference using the same definitions: current 30 days (Sep 1-30) vs prior 30 days (Aug 2-31), inclusive.

Add a **new PySpark cell** to the existing notebook and run:

```python
from pyspark.sql import functions as F

signals = (
    usage
    .withColumn("snapshot_date", F.to_date("snapshot_date"))
    .withColumn(
        "seat_utilisation",
        F.when(
            F.col("licensed_seats") > 0,
            F.col("active_users") / F.col("licensed_seats")
        )
    )
)

current = F.col("snapshot_date").between("2025-09-01", "2025-09-30")
prior = F.col("snapshot_date").between("2025-08-02", "2025-08-31")

averages = signals.agg(
    F.count(F.when(current, 1)).alias("current_days"),
    F.count(F.when(prior, 1)).alias("prior_days"),
    F.avg(F.when(current, F.col("active_users"))).alias("active_users_current_avg"),
    F.avg(F.when(prior, F.col("active_users"))).alias("active_users_prior_avg"),
    F.avg(F.when(current, F.col("api_calls"))).alias("api_calls_current_avg"),
    F.avg(F.when(prior, F.col("api_calls"))).alias("api_calls_prior_avg"),
    F.avg(F.when(current, F.col("seat_utilisation"))).alias("seat_util_current_avg"),
    F.avg(F.when(prior, F.col("seat_utilisation"))).alias("seat_util_prior_avg"),
)

def decline_pct(prior_name, current_name):
    return F.when(
        F.col(prior_name) > 0,
        (F.col(prior_name) - F.col(current_name)) / F.col(prior_name) * 100
    )

reference = (
    averages
    .withColumn(
        "active_users_decline_pct",
        decline_pct("active_users_prior_avg", "active_users_current_avg")
    )
    .withColumn(
        "api_calls_decline_pct",
        decline_pct("api_calls_prior_avg", "api_calls_current_avg")
    )
    .withColumn(
        "seat_utilisation_decline_pct",
        decline_pct("seat_util_prior_avg", "seat_util_current_avg")
    )
)

print("Windows: current 2025-09-01..2025-09-30; prior 2025-08-02..2025-08-31")
display(reference)
```

Expected coverage is 30 rows in each window. If either count is not 30, stop; do not interpret a partial-window comparison as a full 30-day signal. Share the output table. This writes nothing and sends no events.

## Team update protocol

After each user-visible milestone:

1. Record the task ID, status, date, owner, evidence location, and limitation in this file.
2. Update `PROJECT_MEMORY.md` if a durable architecture, data, or operational fact changed.
3. Keep secrets and raw private customer payloads out of Git.
4. Commit/push the board and related safe evidence so teammates share the same state.
