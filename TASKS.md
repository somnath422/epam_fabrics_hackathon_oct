# Team task board

Updated: November 11, 2026. This is the shared source of truth for progress. Update task status only when the stated evidence exists; do not mark a planned item complete because it appears in a diagram or pitch. Keep one task at a time with the user-facing builder, and capture screenshots/exports for cloud-only work.

## Status key

- **DONE** — implementation and evidence verified.
- **PARTIAL** — a useful portion works; acceptance below is not yet met.
- **READY** — next actionable task; not started.
- **BLOCKED** — requires an external permission, artifact, or decision; record the blocker.

## Verified progress

| Workstream | Status | Verified evidence |
|---|---|---|
| Synthetic source and Lakehouse Bronze/Silver/Gold foundation | **DONE** | 6,669,117 source rows; seven Silver entity tables, two Gold foundation tables, validation checks documented in `PROJECT_MEMORY.md`. Synthetic-data limitations remain. |
| Churn model and held-out evaluation | **DONE** | Saved Spark logistic-regression pipeline; account/time-disjoint test; metrics and signed contributions documented in `PROJECT_MEMORY.md`. Separate demo registry version 1 reload/parity and metric persistence verified; active release unchanged. |
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
| T03 | Add versioned behavioral segmentation and membership history | Irfan + Archi | **DONE** | T01 signal definitions | `gold_behavioral_segment_history_demo` holds 15,236 memberships across Nov 30 (7,702) and Dec 30 (7,534), 2025, with provisional rule version, evidence, hash and run metadata. Repeat writes preserved counts with zero duplicate keys; December compared unchanged against Delta version 0 after November insertion. Manual synthetic demo only; no schedule or production approval claimed. |
| T04 | Register the existing model and persist complete metrics | Irfan | **DONE** | Confirm Fabric ML registry support; preserve active release | Demo registry version 1 reload verified; 100-row probability parity has maximum difference 0.0; complete test metrics and definitions persisted and read back from MLflow; active release unchanged. Full signed-contribution reconstruction passed on 100 registered-model rows, maximum probability error 1.4051260155412137e-16. |
| T05 | Confirm Direct Lake mode and apply available Purview labels | Lokesh + Somnath | **PARTIAL** | Organizational labeling support; approved restricted test identity | Screenshots confirm Direct Lake for both semantic-model tables. Model sensitivity label is disabled by organizational settings and shows No label; report label status unverified. Restricted-access test deferred by user; permissions unchanged. Field-level classification inventory remains open. Do not claim Purview labeling or tenant isolation verified. |
| T06 | Approve a risk-based retention marketing playbook | Archi | **READY** | Supported signals/segments from T01/T03 | Small approved strategy set with eligibility, evidence, audience/channel, consent/suppression, owner/approver and success measure. No generic discount assumption or automatic outreach. |
| T07 | Build grounded agent-assisted retention brief | Somnath + Sujith + Archi | **READY** | T01, T03, T04, T06; verify Copilot Studio access first | Supported account query and cited brief use approved read-only data/playbooks; unauthorized/missing/stale evidence is denied or abstained; CSM/Marketing approval required; task and notification states are distinct. |
| T08 | Export cloud implementation and run end-to-end acceptance | Somnath + all owners | **READY** | Each workstream's exports | Sanitized notebooks/configs/metrics/report/KQL/ontology evidence in approved repo; positive, duplicate, stale, unauthorized, failure and retry paths checked; no credentials committed. |
| T09 | Rehearse and submit the 5–10-minute judge demo | Archi + Somnath | **READY** | T08 and organizers' confirmed submission instructions | One timed rehearsal, backup recording/screenshots, consistent labels and counts; clearly distinguishes synthetic historical proof from future capabilities. |

## Current next action: T06, define and approve the demo retention playbook

T05 inspection is finished for now (November 10-11, 2026); incomplete governance acceptance remains open rather than blocking independent playbook work. In `sm_customer_intelligence`, both `gold_report_portfolio` and `gold_retention_actions` show Direct Lake in table properties. The model's sensitivity-label settings show No label and the banner "This setting is turned off because your organization has stopped supporting it." No label option was visible in the report settings inspected; report labeling is unverified. Workspace role inspection showed Admin roles only; the user deferred restricted-access testing for the demo. No permissions or labels were changed. Resume classification inventory, label application if enabled, and approved restricted-access tests separately; do not claim least-privilege enforcement, tenant isolation, or Purview classification from this inspection.

T01 is complete. The user created and saved a bounded synthetic historical usage replay in `customer_usage_observations_demo`, verified its 121 rows / 121 unique events for one account from June 2 through September 30, 2025, and saved the KQL comparison query `usage_journey_001_degradation`. KQL and Spark use inclusive windows of Aug 2-31 and Sep 1-30, with 30 observations each. The observed averages match: active users 12.6667 to 6.4, API calls 1900.1333 to 951.3667, and seat utilization 30.89% to 15.61%; declines are approximately 49.47%, 49.93%, and 49.47%, respectively.

The usage observations are a synthetic historical replay, not live inference or production telemetry. The new table is separate; do not alter `customer_risk_events`, its Eventstream route, or Activator source. The cloud notebook/query have not been exported to Git.

T02 is complete using the source profile and synthetic fixture executed in `09_identity_match_quality_demo`. Silver profile: 10,000 account rows and 10,000 contact rows; unique `(tenant_id, account_id)` on both; zero orphan contact account keys; zero `account_id` reuse across tenants; zero duplicate non-empty domains within a tenant; and one contact row per account. The contact source has no email, so no email-based identity claim is made.

Canonical rule: auto-match only when both `tenant_id` and `account_id` are present and their exact pair resolves to exactly one catalog row. Duplicate exact keys, missing tenant, missing account, and domain-only evidence are not automatically linked; domain candidates are only review suggestions scoped to a supplied tenant, and ambiguous domains require review. Never match across tenants. On the separate eight-record synthetic fixture, results were TP=2, FP=0, FN=3 (100% precision, 40% recall); duplicate-key, missing-tenant, domain-candidate, ambiguous-domain, and unmatched cases were observed, and a cross-tenant lookalike remained unmatched. These metrics characterize only the deliberately constructed fixture, not production or multi-source match quality. Notebook evidence remains cloud-only.

T03 is complete in cloud notebook `10_behavioral_segmentation_demo`. The user accepted proposed v1 thresholds for demo use: usage/API change <= -25%, critical tickets >= 2 or approximate TTR >= 5 days, and days since CSM touch >= 21 or no-show rate >= 0.25. Two or more categories yield Mixed risk; otherwise use the single category or Monitor, with incomplete evidence labeled Insufficient Data. The rule remains `behavioral_v1_provisional`, separate from model risk bands. Each date uses two adjacent 30-day usage windows and as-of support/interaction observations; duplicate/missing/negative usage checks passed.

| Segment | Nov 30, 2025 | Dec 30, 2025 |
|---|---:|---:|
| Adoption decline | 5 | 0 |
| Mixed risk | 177 | 9 |
| Monitor | 5,888 | 5,789 |
| Relationship gap | 1,614 | 1,717 |
| Support distress | 18 | 19 |
| Total | 7,702 | 7,534 |

Memberships are insert-only by `(tenant_id, account_id, as_of_date, rule_version)` in the separate `gold_behavioral_segment_history_demo` table. Persisted evidence/hash, run ID, timestamp and synthetic/historical/provisional flags support audit. Repeat writes left 15,236 rows and zero duplicate keys; an exact row comparison proved December unchanged from Delta version 0 after November was added. This is a manual historical demo, not scheduled segmentation or production-ready concurrency validation. Only accounts with an observation on the as-of date are covered. Existing risk/report/Activator paths were not modified; the notebook has not been exported to Git.

T04 registration and metric persistence are verified in `nb_03_train_evaluate`: model `customer_intelligence_churn_lr_registry_demo`, version 1, MLflow run `c4c184ee-8db3-45ee-be9c-c068eb21937d` in experiment `customer_intelligence_churn_registry_demo`. The registered Spark pipeline reloaded with all 13 inputs; probabilities matched the original pipeline exactly on 100 feature-ready September 30, 2025 rows. Original held-out metrics from evaluation run `86e5303d-70c6-47e7-b3f4-6efafa226320` were copied/derived and verified in the registration run, with definitions at `evaluation/test_metric_definitions.json`. These cover 21,178 Monday test snapshots (1,136 positive), July 7-September 29, 2025: accuracy 98.956464%, always-negative baseline 94.635943%, precision/prevalence lift 18.443219x, plus precision, recall, F1, Spark PR-AUC and confusion counts. This was not a registered-model full test-set rerun. Dependency inference fell back to Fabric's Spark requirement; no input signature/example was logged, and portability outside this Fabric runtime is unverified. The existing active release still points to `Files/models/churn_lr_v1`, with High 0.05 and Medium 0.03. Full signed-contribution reconstruction using registered-model imputation baselines and all 13 coefficients passed on 100 historical rows, maximum probability error 1.4051260155412137e-16 (tolerance 1e-12). This is mathematical reconstruction, not SHAP or causal evidence. T04 is complete; notebook updates remain cloud-only.

## Team update protocol

After each user-visible milestone:

1. Record the task ID, status, date, owner, evidence location, and limitation in this file.
2. Update `PROJECT_MEMORY.md` if a durable architecture, data, or operational fact changed.
3. Keep secrets and raw private customer payloads out of Git.
4. Commit/push the board and related safe evidence so teammates share the same state.
