# Project memory: Customer Intelligence Engine

Last updated: November 10, 2026.

This is the shared engineering handoff and continuation baseline. Read it before changing the project or asking an AI assistant to continue work. It records confirmed demo progress from the build sessions; it is not a fresh inspection of the live tenant. Current capacity, rule, connection, and job status must be checked in Fabric.

## 1. Purpose and status

Build a Microsoft Fabric early-warning system for B2B SaaS accounts: predict churn within the next 90 days, explain risk, segment accounts, propose human-reviewed retention plays, and persist review tasks.

**Implemented demo loop:** synthetic CSV -> Bronze -> Silver -> Gold -> trained model -> saved daily scores and explanations -> Power BI -> historical score replay -> Eventstream -> Eventhouse/KQL -> Activator -> notebook -> durable retention task -> Power BI.

| Area | Confirmed progress | Boundary |
|---|---|---|
| Data | 10,000 accounts, 730-day source window; typed entities and trailing features | Synthetic, with known subscription-date defects |
| ML | Saved logistic-regression pipeline; account/time-disjoint evaluation | Synthetic held-out results, not production generalisation |
| Explanations | Full signed contributions reconstruct every scored probability | Not causal and not SHAP |
| Reporting | Portfolio Overview, Account History, Retention Actions | Read-only task status; navigation is not automatic account drillthrough |
| Streaming | Seven saved scores ingested and inspected | Historical replay, not online inference |
| Automation | Event-level Activator rule launched handler and created task | Startup/polling delays; no immediate-response SLA |
| Task preservation | Snapshot publication retry preserved existing task and status | Sequential evidence, not concurrent exactly-once proof |
| Notifications | Task exists and can be seen in Power BI | No email or Teams delivery; sandbox mailbox/licensing blocked it |
| Presentation | Editable 26-slide PPTX delivered | Future copilot is clearly labelled as a concept |

The earlier blueprint, role guides, demo script, and submission wording contain planned work. Where they differ from confirmed status, use this file as the continuation baseline and verify the live item before making claims.

## 2. What is saved, and what is not

### In this repository

- [Generator](./generate_master_csv.py): chunked CSV generation with seed 42.
- [Ingestion/Gold guide](./build/09_Setup_Ingestion_Gold_Guide.md): runnable Fabric notebook cells and checks for the data foundation.
- [Replay sender](./send_replay_events.py): hidden credential prompt, WebSocket transport, validation-only mode, phased replay.
- [Replay data](./schema_setup_001.jsonl): seven synthetic, saved model outputs, not fabricated risk fixtures.
- [Shared contracts](./build/02_Shared_Contracts_and_Acceptance.md), role guides, blueprint, and submission material.
- [Judges' deck](./submission/Customer_Intelligence_Engine_Judges_Deck.pptx): native editable shapes, two editable charts with embedded workbooks, screenshots, and presenter notes.

Deck validation passed: 26 slides, notes, two chart/workbook pairs, embedded screenshots, well-formed XML, and all shapes within slide bounds. Text received conservative fallback-font fit checks. Native PowerPoint rendering was not validated. Screenshots remain raster images; charts, text, and diagrams are editable.

### Not yet exported into this repository

The complete executed ML/scoring/publication/replay/handler notebooks, model directory, evaluation/release table contents, Power BI artifacts, KQL/streaming/Activator deployment definitions, and full cloud evidence are **not** versioned here. The data guide alone does not recreate the full deployed system. Do not invent missing notebook source from this summary or call it a tested deployment.

The CSV remains local under `output/` and was uploaded to the Lakehouse. Git excludes generated output, virtual environments, caches, and local secret files. Do not commit credentials, connection strings, sandbox access passes, or unrestricted raw logs.

## 3. Fabric inventory

Names below identify the existing demo; another tenant must create its own resources and update references.

| Item | Name or location |
|---|---|
| Existing assigned capacity | `capacity2447013` |
| Workspace | `ws_customer_intelligence` |
| Lakehouse | `lh_customer_intelligence` |
| Uploaded source | `Files/master_saas_b2b_daily_10k_2y_2024.csv` |
| Training notebook | `nb_03_train_evaluate` |
| Scoring notebook/workstream | `04_score_explain`; confirm exact item name in workspace |
| Report/task publication notebook | `05_publish_actions_reports` |
| Replay preparation notebook | `06_replay_scored_events` |
| Alert handler notebook | `07_handle_risk_alert` |
| Saved pipeline | `Files/models/churn_lr_v1` |
| Model version | `churn_lr_v1` |
| Evaluation run | `86e5303d-70c6-47e7-b3f4-6efafa226320` |
| Active demo release | `churn_lr_v1_86e5303d-70c6-47e7-b3f4-6efafa226320` |
| Semantic model | `sm_customer_intelligence` |
| Power BI report | `rpt_customer_intelligence` |
| Eventstream | `es_customer_risk` |
| Custom source | `src_scored_risk_replay` |
| KQL destination | `dest_customer_risk` |
| Eventhouse and KQL database | `eh_customer_intelligence` |
| Event table | `customer_risk_events` |
| Real-Time Dashboard | `rtd_customer_risk_replay` |
| Working event-level Activator rule | `eh_customer_intelligence event alert` (default UI name) |
| Old property-level rule | `demo_high_risk_review`; intentionally left stopped |

Core Delta tables:

- Bronze: `bronze_master_daily`.
- Silver: `silver_account`, `silver_contact`, `silver_subscription_daily`, `silver_usage_daily`, `silver_support_daily`, `silver_interaction_daily`, `silver_churn_outcomes`.
- Gold foundation: `gold_customer360_daily`, `gold_training_outcomes`.
- Operational/reporting: `gold_account_risk`, `gold_report_portfolio`, `gold_retention_actions`.
- Coverage, split, evaluation, and release tables also exist in the cloud workflow; export notebooks to recover their exact names and schemas.

## 4. Data foundation and invariants

- Source: 41 columns, **6,669,117 rows**, 10,000 accounts, January 1, 2024 through December 30, 2025 inclusive (730 days).
- 2,471 eventual churners (24.7%). Churned accounts stop after the cancellation-day row, so the file is smaller than the original 7.3-million-row full-grid target.
- Raw positive labels: 222,390; negatives: 6,446,727.
- Exclude cancellation day from the eligible at-risk population.
- Source support/contact rolling metrics are approximate. Tenant IDs are effectively unique per account, not a realistic multi-account tenant hierarchy.
- Known source date defects: 2,434,753 subscription-before-account rows and 743,379 subscription-starts-later rows. Combined invalid subscription-date flag: 3,178,132; valid: 3,490,985. Do not silently repair them. Invalid `days_to_renewal` is null.
- `feature_ready`: 6,079,117 true; 590,000 false. Require at least 60 days of history and `at_risk_population`.
- Trailing features use calendar-date windows, including current 30 days versus previous 30 days; no future window.
- Never use `will_churn`, `churn_date`, `cancel_date`, `days_to_churn`, `subscription_status`, or the label as model predictors. Keep outcome tables out of operational reports.
- Bronze/Silver/Gold counts, keys, types, continuity, outcome matching, and blocking business rules passed during the guided build.
- Historical truncation check: `ACC000003`, snapshot June 21, 2025, no differences observed. This is one checked case, not universal leakage proof.

Do not change source dates, split membership, or label policy without a new version and rerun of downstream acceptance checks.

## 5. ML, evaluation, and reporting baseline

### Model and split

Median imputation fitted on training only -> VectorAssembler -> Spark LogisticRegression (`maxIter=100`, `regParam=0.1`, `elasticNetParam=0`, `standardization=True`).

Account bucket: `pmod(xxhash64(account_id), 10)`. Training/evaluation use Monday snapshots:

| Partition | Buckets | Period | Rows | Accounts | Positive rows |
|---|---|---|---:|---:|---:|
| Train | 0-5 | March-September 2024 | 187,671 | 6,084 | 4,129 |
| Validation | 6-7 | January-March 2025 | 22,474 | 1,771 | 965 |
| Test | 8-9 | July-September 2025 | 21,178 | 1,679 | 1,136 |

Thirteen features:

```text
seat_utilisation_30d, active_users_avg_7d, active_users_avg_30d,
sessions_avg_30d, usage_change_30d, api_change_30d,
advanced_feature_share_30d, critical_tickets_avg_7d,
tickets_created_30d, avg_ttr_days_60d, interactions_30d,
days_since_last_csm_touch, no_show_rate_90d
```

High threshold: **0.05**, selected by best unrounded validation F1 among 17 tested thresholds. Medium starts at **0.03**, explicitly approved for the demo. These are not 0.5/0.3. High takes precedence over Medium.

Validation PR-AUC: 0.8787. At High: 786 flagged, 774 TP, 12 FP, precision approximately 98.5%, recall 80.2%. Medium-only: 119 rows, 38 TP, 81 FP (31.9% precision). Do not use the cumulative Medium-or-High precision to describe Medium alone.

### Held-out test evidence

| Metric | Value |
|---|---:|
| Spark `areaUnderPR` (not average precision) | 0.8996953376829092 |
| Precision at High | 0.9893048128342246 |
| Recall at High | 0.8142605633802817 |
| F1 at High | 0.8932882665379044 |
| TP / FP / FN / TN | 925 / 10 / 211 / 20,032 |
| Flagged rows | 935 (4.41496%) |

Unique-account view: 1,679 test accounts; 179 with positive snapshots in the test window; 152 detected, 27 missed. Of 153 flagged accounts, one had no correct alert. Detection rate: 84.92%.

Among detected accounts only, first correct alert observed during the test period had lead time min 3, mean 50.6, median 54, max 90 days; 113 had at least 30 days and 65 at least 60 days. This is not lifetime-first detection and does not guarantee 90-day warning for every churner.

### Daily reporting and explanations

Daily held-out scoring covers buckets 8-9, July 1-September 30, 2025: 150,127 snapshots, 1,685 accounts, 92 dates.

September 30 portfolio: **1,582 scored / 7,982 eligible (19.82% coverage)**; 55 High, 5 Medium, 1,522 Low. All-date row bands: 6,722 High, 1,194 Medium, 142,211 Low. Do not confuse daily report counts with Monday evaluation counts or whole-portfolio coverage.

Contribution for each feature: coefficient times (imputed value minus training median). Reference logit is intercept plus the sum of coefficient times training median. All signed terms reconstruct the score; 150,127 checks passed, maximum absolute probability error `6.661338147750939e-16`. Displayed top-three positive contributors alone do not reconstruct it.

Segments map strongest contributors to transparent demo plays. September 30 High: 54 Support friction, one Engagement gap. Plays require human review; no intervention efficacy was measured. `ARR * score` is an uncalibrated prioritisation proxy, not expected revenue loss.

### Power BI details to preserve

- Pages: Portfolio Overview, Account History, Retention Actions.
- Portfolio page is filtered to September 30; High filter applies only to the account table, not full-cohort cards.
- Account History has a single-account slicer, daily score and usage curves, newest-first details, scores displayed to four decimals.
- Retention action table is disconnected from portfolio filtering and filtered explicitly by release/scenario.
- `Scored Accounts = DISTINCTCOUNT('gold_report_portfolio'[account_id])`.
- `High Risk Accounts = CALCULATE([Scored Accounts], 'gold_report_portfolio'[risk_band] = "High")`.
- State synthetic data, limited scored cohort, uncalibrated scores, and historical dates explicitly. Preserve these disclosures.

## 6. Replay and automated action contract

### Saved replay

The committed JSONL contains seven actual saved scores for `ACC008178`, tenant `TEN008178`, replay `schema_setup_001`. `is_fixture=false` means model output; it does not mean real customer data. `is_synthetic=true` and `is_historical_replay=true` remain required.

| Historical date | Score (rounded) | Band |
|---|---:|---|
| 2025-07-01 | 0.0061023 | Low |
| 2025-07-15 | 0.0158391 | Low |
| 2025-08-01 | 0.1036268 | High |
| 2025-08-15 | 0.4413370 | High |
| 2025-09-01 | 0.8845317 | High |
| 2025-09-15 | 0.9894135 | High |
| 2025-09-30 | 0.9981330 | High |

Use the JSONL for exact scores, not rounded values above. Stable event IDs identify saved release/replay/account/snapshot. `event_time` is historical; the sender adds `emitted_at` as current UTC. The KQL schema has 17 typed fields including that added timestamp.

The original schema replay was observed as seven stored rows, seven unique IDs, zero duplicates. This does not guarantee duplicate-free future ingestion.

### Activator path

- Property-level rule did not expose needed dynamic event fields. The working rule is **event-level**.
- High condition is `model_score >= 0.05`.
- Run Notebook points to `07_handle_risk_alert`.
- Map five **String** parameters to the notebook's parameter cell:

| Parameter | Event field |
|---|---|
| `alert_account_id` | `account_id` |
| `alert_object_id` | `object_id` |
| `alert_snapshot` | `historical_snapshot` |
| `alert_replay_sent_at` | `replay_sent_at` |
| `alert_model_score` | `model_score` |

The demo object is `TEN008178|ACC008178|alert_demo_001`. The handler validates identity, the allowlisted replay, parsed dates/score, exactly one active release, exact saved Gold snapshot, matching score within `1e-8`, High band, owner, and play before writing.

Handler notebook cell sequence: parameter defaults -> validation function -> task-writing function -> invocation. Function-definition cells printing "No tasks written" are expected. Do not run only the final cell in a fresh session; its parameters/functions will not exist.

Task insert is an insert-only Delta MERGE. Event action identity includes release/scenario/tenant/account/model, not snapshot, yielding one task per replay object. Scenario: `event_replay_alert_demo_001`. This deliberately does not implement production cooldown or reopening.

Original snapshot scenario: `historical_snapshot_2025_09_30_v1`; 55 tasks (54 Open, one In progress). Original `ACC008178` September 30 task was manually set to In progress; rerunning snapshot publication preserved it.

The automatic August 1 event created a separate Open task for the same account, owner `csm_017`, without changing the original task. Expected combined selected-scenario total after that run: 56 tasks.

Confirmed event action ID:
`c1a161a9531b7d7a3550908ae3e5e51943ca20d5c82cefcd8172f8c1dd89075d`.

The successful automated run log said `Action outcome: Created`, `Notification status: Not attempted`, and `Event-triggered retention task verified.` Monitoring initially showed Starting/Not started even while execution progressed. Inspect stdout and the resulting Delta row rather than assuming failure or resubmitting immediately.

### Dashboard query and duplicate caveat

The demo query used latest historical snapshot per object with a one-hour emission filter. Repeated same-event deliveries can tie on historical time. For a future query revision, deduplicate on latest emission first, then choose latest historical state:

```kusto
customer_risk_events
| where replay_run_id == "alert_demo_001"
| summarize arg_max(emitted_at, *) by event_id
| summarize arg_max(event_time, *) by object_id
| where emitted_at > ago(1h)
| project object_id, account_id,
    historical_snapshot=event_time, replay_sent_at=emitted_at,
    model_score=risk_score, risk_band, top_driver_1, recommended_play
```

This revised query is a recommendation, not a confirmed deployed change. Validate it in KQL and recheck all five event mappings before replacing the current rule source. Event-time ties across different event IDs still need a defined production policy.

The one-hour query window is not a handler-level freshness/replay guard. Add and test such a guard before production. Dashboard polling was five minutes; observed end-to-end startup delay was substantial (roughly 12 minutes), not a measured SLA.

## 7. Local setup and safe replay

Run commands in a terminal from the repository root, not in the Python `>>>` REPL or inside a `.py` file. No Fabric capacity is needed for validation-only commands.

### macOS/Linux

```bash
python3 -m venv .venv-replay
.venv-replay/bin/python -m pip install azure-eventhub websocket-client
.venv-replay/bin/python send_replay_events.py --validate-only
.venv-replay/bin/python send_replay_events.py --alert-phase low --validate-only
.venv-replay/bin/python send_replay_events.py --alert-phase high --validate-only
```

### Windows PowerShell

```powershell
py -m venv .venv-replay
.\.venv-replay\Scripts\python.exe -m pip install azure-eventhub websocket-client
.\.venv-replay\Scripts\python.exe .\send_replay_events.py --validate-only
.\.venv-replay\Scripts\python.exe .\send_replay_events.py --alert-phase low --validate-only
.\.venv-replay\Scripts\python.exe .\send_replay_events.py --alert-phase high --validate-only
```

For **authorised live rehearsal only**, remove `--validate-only` from the chosen invocation. Default sends all seven schema events. `--alert-phase low` sends July 15 under `alert_demo_001`; inspect ingestion and rule state before `--alert-phase high` sends August 1. Reusing the replay can preserve the existing task rather than produce a new one.

The sender prompts for the Event Hub-compatible connection string without echo and optionally the entity name. Use a real local terminal; Fabric notebook `getpass()` and widget attempts hung in this environment. Transport uses secure WebSockets on port 443, requiring `websocket-client` in addition to `azure-eventhub`. Never paste credentials into source, chat, shell arguments, or committed files.

Endpoint acceptance is not proof of Eventhouse ingestion or task delivery. Verify each stage before retrying; uncertain sends can duplicate deliveries. Live replay can incur compute and trigger configured actions.

### Regenerate the CSV only when needed

```bash
python3 -m venv .venv-data
.venv-data/bin/python -m pip install pandas numpy
.venv-data/bin/python generate_master_csv.py
```

PowerShell equivalent: `py -m venv .venv-data`, then use `.\.venv-data\Scripts\python.exe` for the install and script commands above.

Output is `output/master_saas_b2b_daily_10k_2y_2024.csv` beside the generator. Generation writes in account batches and overwrites that output; preserve any required existing copy first. It requires roughly 1.7 GiB of disk space. Do not push this file to GitHub. Seed 42 is fixed, but dependency versions are not pinned; compare the produced counts/schema to the recorded baseline rather than assuming byte-identical output on every environment.

For Fabric ingestion use the actual root `Files/` upload path above, not the optional `Files/bronze/` path shown in the original setup instructions.

## 8. Failure lessons and budget-safe operations

| Symptom | Confirmed lesson |
|---|---|
| Spark capacity error 430 / queued jobs | Stop idle old sessions, coordinate shared capacity, reuse an appropriate session; do not resize reflexively |
| Eventhouse wizard cannot infer schema | It needs events; complete Configure KQL data connection after save/publish, then confirm mapping and ingestion |
| `ModuleNotFoundError` involving WebSockets | Install `websocket-client` in the same interpreter environment as the sender |
| Activator only exposes `model_score` | Use the event-level rule to expose all required fields |
| Alert threshold mistakenly 0.5 | Correct demo High threshold is 0.05 |
| Notebook displays Starting/Not started for a long time | Inspect monitoring logs and output rows before rerunning |
| Function ready / no tasks written | Definition cells only; the mapped invocation creates the task |
| Outlook mailbox/license error; Teams unavailable | No notification evidence; use the verified notebook-to-task path, contact sandbox support rather than buying licences |
| Power BI counts unexpectedly shrink | Clear cross-selections; keep High as table-only filter and preserve date/coverage context |

The sandbox budget is $100. The last user-reported spend was $76 on November 6, not a current balance. Check current usage before restarting compute. Do not create a replacement capacity, upgrade SKU, provision Azure OpenAI, or buy licences just to reproduce the demo.

After coordinated rehearsals: stop Activator rules, stop streaming ingestion as appropriate, stop notebook Spark sessions, and pause the assigned capacity only when no teammate needs it and permissions allow. Stopping the local sender alone does not stop cloud services. Pausing can affect availability; storage and other resources may still cost money. No cloud resources were stopped or changed by this repository handoff.

## 9. Export and reproducibility checklist

Complete this before sandbox expiry or claiming that a teammate can rebuild the entire demo from Git:

1. Export every executed notebook, including the complete ML/scoring/action/replay/handler chain. Preserve handler parameter-cell metadata. Review and remove secrets and credential-bearing outputs.
2. Export exact feature order, training medians, pipeline settings, split construction, threshold search, release configuration, model artifact location, and evaluation results. Use approved artifact storage for large binaries.
3. Export Delta schema/DDL contracts and safe small evidence samples; never dump credentials or real customer data.
4. Export KQL table/mapping/query definitions and document Eventstream connection and Activator rule/parameter setup without SAS strings.
5. Export the semantic model/report in a supported editable format, including measures, relationships, report filters, and disclosures.
6. Preserve sanitised task/run evidence with separate historical and operational UTC timestamps. The PPT screenshots are presentation evidence, not deployment definitions.
7. Rebuild in an authorised clean environment using approved identities; run data acceptance, split/leakage checks, score reconstruction, replay validation, task-preservation tests, and report checks.
8. Pin dependencies after testing in the intended environment; document Fabric runtime and any preview/licensing requirements.

Keep all exports in approved repository/storage locations. Do not commit account credentials, access passes, connection strings, or hidden notebook authentication material.

## 10. Extension roadmap

### First: preserve and harden the working baseline

- Complete exports above and synchronise old plan/submission wording with verified delivery.
- Add automated tests for handler validation, negative inputs, deterministic IDs, existing-task preservation, stale events, and concurrent duplicate execution.
- Define retries, deduplication, cooldown, reopening, cancellation, ownership, failure monitoring, and audit history before widening replay beyond the demo allowlist.
- Re-test source quality/leakage across representative accounts and dates. Correct synthetic date generation only in a new dataset/model release.
- Expand scoring beyond held-out buckets using an explicit deployment/evaluation policy. Never relabel current 19.82% coverage as whole-portfolio deployment.
- Establish calibration, monitoring, RLS/identity enforcement, and real-data validation; none is proven by synthetic metrics.

### Future grounded Customer Intelligence Copilot

Not implemented. Candidate Fabric Data Agent / Copilot Studio integration is subject to tenant permissions and licensing; no additional spend is authorised by this plan.

Supported future questions could include "Which High-risk accounts belong to my team?", "Why did this account's score rise?", or "What saved review tasks are open?" Do not promise to answer any question.

The business analyst additionally proposed AI-assisted, risk-based retention-marketing strategy suggestions. This is future scope, not a feature in the current demo. A safe design would map supported risk evidence to approved playbooks (for example usage decline -> adoption/onboarding support; support friction -> coordinated service recovery; low engagement -> owner-led value review), state audience/channel/assumptions, respect consent and suppression policies, and require CSM/Marketing approval. Do not autonomously send campaigns. Measure incremental uplift against a control before claiming effectiveness or ROI.

Design:

1. Authenticate caller and enforce identity/RLS at every tool/data access boundary.
2. Use governed read-only SQL/DAX tools over approved operational/report tables for numeric answers.
3. Retrieve only approved playbooks/campaign strategies for qualitative guidance, not arbitrary documents or future outcome labels.
4. Cite release, snapshot date, metric denominator, cohort coverage, and source evidence.
5. Abstain on unsupported questions or missing/stale data; separate model associations from causal explanations.
6. Require explicit CSM/Marketing approval for any strategy, task mutation, offer, or outreach; start read-only.
7. Test permission isolation, prompt injection, metric accuracy, unsupported-answer refusal, freshness, latency, and cost before a demo.

Additional later work: measured intervention outcomes, prospective evaluation, incremental scoring, proper CRM integration, and licensed notification delivery. No retained-revenue or intervention-uplift claim is supported yet.

## 11. Continuing this project

For a teammate or AI assistant:

> Read README.md, PROJECT_MEMORY.md, and build/02_Shared_Contracts_and_Acceptance.md first. Distinguish implemented synthetic-demo evidence from planned production capabilities. Inspect current Git and Fabric state before changing it. Preserve release/cohort/date context, leak-free features, signed contribution checks, deterministic task identity, existing task status, and explicit synthetic/historical disclosures. Never request or commit credentials. Do not run paid cloud work or replay automatically. Export missing cloud source before calling the repository fully reproducible.

At each handoff update this file with the date, actual changed artifacts, validation commands/results, known gaps, and next bounded steps. Keep secret values and raw private conversation history out of it.

### November 10 repository handoff validation

- `send_replay_events.py --validate-only`: passed, seven saved schema events.
- `send_replay_events.py --alert-phase low --validate-only`: passed, one Low event.
- `send_replay_events.py --alert-phase high --validate-only`: passed, one High event.
- Python AST syntax checks passed for the sender and data generator.
- Local links in the root README, this handoff, and team handbook resolved.
- Saved PPTX reopened with 26 slides; ZIP integrity passed.
- `git diff --check` passed; generated CSV, local environment, and Python cache exclusions were verified.
- These checks did not send events, rerun large data generation, or execute paid Fabric jobs.

### November 10 judges' criteria audit

The supplied judging rubric weights Business Value 25, Technical Excellence 20, Solution Quality 25, Innovation 15, and Presentation & demo 15. Detailed status and a corrected rehearsal checklist are in [Judges_Readiness_and_Gap_Review.md](./submission/Judges_Readiness_and_Gap_Review.md).

Against the team's seven target capabilities, only the base data/score/event/task/report flow is demonstrated. Fabric IQ ontology, true multi-source identity resolution/match-quality evidence, KQL-derived journeys/signals, scheduled auditable segmentation, Fabric ML registry registration, Copilot Studio agent, customer notification delivery, and Purview labels are absent or unverified. Direct Lake mode is unverified. Do not state them as delivered.

From the held-out confusion matrix, accuracy is derivable as 98.96%, baseline always-negative accuracy is 94.64%, and precision/prevalence lift is 18.44x. Treat accuracy and lift as derived values, not separately persisted model metrics. Keep PR-AUC (Spark `areaUnderPR`) and disjoint account/time split context with all claims.

The initial submission text and demo script contained unverified claims about SHAP, MLflow, live usage replay, 90-day account-specific lead, and notification/CRM delivery. They must be corrected against the current evidence before a pitch; see the readiness review. No live tenant inspection, feature build, paid job, or event send was performed for this audit.
