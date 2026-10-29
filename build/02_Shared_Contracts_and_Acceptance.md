# Shared contracts, business rules, and acceptance

[Handbook](./README.md)

Owners: Somnath approves integration contracts; producers own correctness; Archi accepts business definitions. Version 1 is proposed here and must be acknowledged on October 29.

Named owners: Dev 1 = Ashish; Dev 2 = Irfan; Dev 3 = Lokesh; Dev 4 = Sujith.

## 1. Names and ownership

| Item | Name | Writer |
|---|---|---|
| Workspace | `ws_customer_intelligence` | Somnath |
| Lakehouse | `lh_customer_intelligence` | Somnath |
| Ingestion notebook | `01_ingest_validate` | Dev 1 |
| Feature notebook | `02_silver_gold` | Dev 1 |
| Training notebook | `03_train_evaluate` | Dev 2 |
| Scoring notebook | `04_score_explain` | Dev 2 |
| Publication notebook | `05_publish_actions_reports` | Somnath, pairing with Dev 2 |
| Replay sender | `06_replay_scored_events` | Dev 4 |
| Semantic model | `sm_customer_intelligence` | Dev 3 |
| Report | `rpt_customer_intelligence` | Dev 3 |
| Eventstream | `es_customer_risk` | Dev 4 |
| Eventhouse / KQL database | `eh_customer_intelligence` / `kql_customer_risk` | Dev 4 |
| Activator | `act_customer_risk` | Dev 4 |

Schema-enabled Lakehouses may show `dbo.table_name`. Use the default schema consistently; do not create an extra schema unless all consumers are updated.

## 2. Source reality and exclusions

- Source: [master CSV](../output/master_saas_b2b_daily_10k_2y_2024.csv).
- Generator: [Python generator](../generate_master_csv.py).
- Expected source: 41 columns; 6,669,117 rows; 10,000 accounts; Jan 1, 2024-Dec 30, 2025.
- These are expected values from the existing source, to be verified in Fabric.
- Cancellation-day rows exist and have horizon label zero. Exclude them from the at-risk prediction population; they are not useful negative examples.
- `cancel_date` is populated on historical churner rows before cancellation. It is future information and must never enter predictors or operational report views.
- Subscription start dates can lie after snapshots or conflict with account dates. Flag and quarantine invalid derived-date features; do not assume production-valid subscription timelines.
- `tickets_created_30d` is generated as a trailing sum; several other "30d/60d/90d" metrics are approximate synthetic signals, not reconstructed ticket/contact histories.
- `tenant_id` is effectively unique per account in this generator. Tenant isolation is demonstrable, but this is not evidence of a realistic multi-account tenant hierarchy.
- No public-dataset impossibility claim is needed. Say this dataset was chosen because it supports the required scenario.

## 3. Shared feature definitions

Gold key: `(tenant_id, account_id, snapshot_date)`. Type dates as Spark `date`, operational timestamps as UTC `timestamp`, counts as integral types, ratios/revenue as numeric types.

| Feature | Definition |
|---|---|
| `seat_utilisation` | Active users / licensed seats; zero/missing denominator -> null plus quality flag |
| `active_users_avg_7d` | Average over calendar days t-6 through t |
| `active_users_avg_30d` | Average over t-29 through t |
| `usage_change_30d` | `(mean users[t-29,t] / mean users[t-59,t-30]) - 1` |
| `api_change_30d` | Same current/prior 30-day definition using API calls |
| `history_days_available` | Number of observed account snapshots up to t |
| `feature_ready` | At least 60 observed daily snapshots and no critical key/count errors |
| `subscription_dates_valid` | Created <= subscription start <= snapshot and renewal > snapshot |

Use calendar-range windows, not the last 30 rows, unless daily completeness has been proved. Null ratios from no history or zero baselines are not zero decline. Retain nulls and fit imputation on training data only.

Gold features keep account metadata needed for reporting. Training uses an explicit allowlist, not "all numeric columns."

Outcomes belong in `gold_training_outcomes`, joined by the same key only in training/evaluation jobs. Operational reports do not get outcome columns.

## 4. Risk and reporting tables

### `gold_account_risk`

Unique key: `(tenant_id, account_id, snapshot_date, model_version)`.

Required fields:

```text
tenant_id: string
account_id: string
snapshot_date: date
scored_at: timestamp UTC
model_version: string
run_id: string
risk_score: double in [0,1]
risk_band: string [High, Medium, Low]
arr_usd: double >= 0
estimated_arr_exposure: double >= 0
primary_segment: string
top_driver_1: string
top_driver_2: string
top_driver_3: string
recommended_play: string
feature_as_of_date: date
is_fixture: boolean
```

`estimated_arr_exposure = arr_usd * risk_score`. If calibration is not established, call it a risk-weighted prioritization proxy, not expected financial loss.

High means `risk_score >= validation_selected_threshold`. Select and document a lower Medium threshold on validation too. Do not hard-code 0.8 simply because it looks impressive.

Store thresholds, feature version, and selected model in `gold_release_config`; publish one active reporting release. Dev 2 supplies these values, Somnath approves them.

### `gold_report_portfolio`

Flatten the approved risk release with account metadata:

```text
All gold_account_risk fields
+ account_name, industry, region, plan_tier, csm_owner
+ seat_utilisation, active_users_avg_7d, active_users_avg_30d,
  usage_change_30d, api_change_30d, critical_open_tickets,
  days_since_last_csm_touch
```

One version per account/date. It may be a disclosed bounded historical reporting cohort, not necessarily every account on every date. Publish scored-account coverage by date so the report does not imply full-portfolio coverage when only a sample is scored.

Use this single wide table for the beginner BI path; no many-to-many relationships needed.

The beginner report uses this same table for both portfolio and account-history pages. `gold_report_history` is an optional smaller history surface if measured size requires a separate model later; do not introduce it merely to add relationships.

### `gold_report_history`

One row per account/date from the same reporting cohort/release:

```text
tenant_id, account_id, snapshot_date, risk_score,
seat_utilisation, active_users_avg_7d, active_users_avg_30d,
usage_change_30d, api_change_30d, critical_open_tickets,
days_since_last_csm_touch, is_fixture
```

### `gold_retention_actions`

```text
action_id, tenant_id, account_id, trigger_snapshot_date,
model_version, owner, recommended_play, status,
created_at, updated_at, notification_status, replay_run_id
```

Statuses: Open, Assigned, In progress, Closed. Notification status: Not attempted, Accepted, Failed, Unknown. "Accepted" means transport accepted the send, not that a human read it.

Actions are persisted with an idempotent Delta MERGE, not a blind append. Use a deterministic hash of tenant/account/model/trigger date for action identity. A restart of the same replay must not create another action.

One initial action per account/model/approved replay scenario is sufficient for the demo. Production cooldown/reopening needs an explicit policy and durable state. Do not confuse an Activator object's in-session state with durable exactly-once processing.

### `gold_evaluation_summary` and `gold_run_log`

Evaluation: model, split, threshold, metric name/value, sample counts, positive prevalence, population window, run ID.

Run log: run ID, stage, start/end UTC, status, row counts, model/feature versions, error summary. Never store credentials or customer payloads in error text.

## 5. Replay event contract

Use flat JSON for simple Eventstream mapping:

```json
{
  "event_id": "stable-source-event-hash",
  "replay_run_id": "rehearsal-001",
  "object_id": "TEN000001|ACC000001|rehearsal-001",
  "tenant_id": "TEN000001",
  "account_id": "ACC000001",
  "event_time": "2025-08-01T00:00:00Z",
  "emitted_at": "2026-10-29T08:00:00Z",
  "model_version": "approved-version",
  "risk_score": 0.72,
  "arr_usd": 42000.0,
  "top_driver_1": "Example format only: usage declined over the trailing windows",
  "recommended_play": "Adoption review",
  "action_id": "deterministic-action-hash-if-triggered",
  "is_fixture": true
}
```

This is a fixture, not model evidence.

- `event_id`: hash of tenant/account/snapshot/model; stable across transport retries.
- `object_id`: tenant/account/replay run so a deliberate new rehearsal can start with new rule state.
- `event_time`: historical behavior date; preserve it in Eventhouse.
- `emitted_at`: current UTC send time; use as Activator processing timestamp for accelerated historical replay where required.
- Source retries and duplicate sends need application/stateful deduplication; Eventhouse does not enforce uniqueness.
- Eventstream connectors use the protocol/configuration actually exposed by the tenant, not arbitrary HTTP POST.

## 6. Segmentation and business rules

Proposed initial interpretation thresholds, to be approved by Archi; these are not learned churn thresholds:

- Adoption decline: usage or API change <= -25%.
- Support distress: critical open tickets >= 2 or approximate TTR >= 5 days.
- Relationship gap: days since touch >= 21 or no-show rate >= 0.25.
- Mixed risk: two or more conditions.
- Otherwise: Monitor.

Segment labels summarize evidence, not causality. Retention plays require human approval.

## 7. Acceptance suite

| ID | Owner | Test and expected result |
|---|---|---|
| T01 | Dev 1 | Source profile matches expected rows/columns/date span, or discrepancy explicitly resolved |
| T02 | Dev 1 | Duplicate/missing account-date keys -> visible failure |
| T03 | Dev 1 | Features for t unchanged when rows after t are removed |
| T04 | Dev 2 | Forbidden feature and overlapping account groups -> visible failure |
| T05 | Dev 2 | Complete label follow-up; cancellation-day rows excluded from prediction |
| T06 | Dev 2 + Archi | Baseline/model compared on identical held-out population |
| T07 | Dev 2 | Threshold selected only on validation; test not used for tuning |
| T08 | Dev 3 + Archi | One selected date; ARR and account cards reconcile to published table |
| T09 | Dev 3 | RLS role denies other tenant rows for a Viewer; editors are not valid RLS test users |
| T10 | Dev 4 | Same event twice -> one business action; notification duplication behavior measured |
| T11 | Dev 4 | Replay restart/out-of-order delivery -> documented safe behavior |
| T12 | Somnath | Failed/stale scoring does not appear as a fresh successful release |
| T13 | Archi | Notification includes account, historical date, model, drivers, owner, action |
| T14 | Archi | First-alert lead time reconciles to outcomes in evaluation-only view |
| T15 | Somnath | Two clean end-to-end runs and usable exports outside sandbox |

No test is "passed" by writing these instructions. Retain actual outputs.
