# Customer Intelligence Engine

## Idea name

Customer Intelligence Engine: Explainable Churn Signals to Retention Action

## Target industry

B2B SaaS and subscription software

## Business use case

SaaS providers usually discover churn at renewal, when the cancellation is already decided. By then the opportunity to retain the account has passed. The signals that precede that decision — declining seat utilisation, falling API and feature usage, rising critical support tickets, slower resolution times, and a customer success manager who has gone quiet — are spread across product telemetry, the support desk, and CRM, and are rarely converted into a timely, explainable action.

Customer Intelligence Engine unifies these signals into an account-level Customer 360 profile, predicts the probability that an account will churn within the next 90 days, explains why that account is at risk, and recommends a retention play. It is built for a customer success leader who needs to answer three questions: which accounts should we work today, why are they at risk, and what should we do next.

The solution is trained on a purpose-built synthetic B2B SaaS dataset of 10,000 accounts observed daily for two years (6,669,117 account-day snapshots, 2024-01-01 to 2025-12-30). Because the data is a genuine longitudinal event history rather than a point-in-time snapshot, the 90-day early-warning claim is a real, verifiable forward-looking label rather than a reframed aggregate.

## Data foundation

We first evaluated the public BigML telecom churn dataset and rejected it. It is a single flat table of 3,333 rows with no timestamps, no entity relationships, and no event history, so it cannot support a forward-looking 90-day label, a Customer 360 ontology, or a credible Eventhouse demonstration. Retained in `blueprint/archive/` only as a reference benchmark.

We therefore generated our own dataset with `generate_master_csv.py` (reproducible, seeded, chunked writer):

| Property | Value |
|---|---|
| Grain | one row per `account_id` x `snapshot_date` |
| Accounts | 10,000 |
| Observation window | 730 daily snapshots, 2024-01-01 to 2025-12-30 |
| Rows | 6,669,117 (1.7 GB CSV) |
| Columns | 41 across Account, Contact, Subscription, Usage, Support, Interaction, Label |
| Churned accounts | 2,471 (24.7%) |
| Positive label rate | 3.33% of rows (`label_churn_next_90d` = 1) |
| Pre-churn degradation | begins 60-120 days before the cancel date, per account |

Churned accounts stop emitting snapshots on their cancellation date, and every churner has a full 90-day labelable runway, so there is no look-ahead leakage in the label definition.

The degradation is real and measurable, which is what makes the model trainable and the explanations defensible. Mean values of the modelling features, split by the 90-day label:

| Signal | Label 0 | Label 1 | Change |
|---|---|---|---|
| `active_users` | 69.59 | 43.86 | -37.0% |
| `sessions` | 199.81 | 124.34 | -37.8% |
| `api_calls` | 6499.11 | 4207.68 | -35.3% |
| `interactions_30d` | 6.00 | 3.80 | -36.6% |
| `critical_open_tickets` | 0.08 | 0.86 | +961% |
| `tickets_created_30d` | 11.03 | 21.43 | +94% |
| `avg_ttr_days_60d` | 1.80 | 5.46 | +203% |
| `days_since_last_csm_touch` | 13.00 | 19.67 | +51% |
| `no_show_rate_90d` | 0.04 | 0.24 | +467% |

## Business impact

The solution moves retention from a renewal-day reaction to a targeted early-warning workflow. It identifies high-risk accounts, provides an understandable reason for each alert, and creates a recommended next action instead of delivering another passive report.

Expected business outcomes:

- Up to 90 days of advance warning before an account cancels, giving customer success a real intervention window instead of a renewal-day surprise.
- More focused retention spend by ranking accounts by expected revenue at risk (`arr_usd` x churn probability) and tailoring the play to the actual drivers.
- Improved trust and adoption because every score is accompanied by business-readable drivers.
- A reusable Fabric accelerator for other early-warning scenarios such as expansion-opportunity detection, payment risk, and service-quality escalation.

Impact will be measured on an out-of-time, out-of-account holdout using ROC-AUC, PR-AUC, precision, recall, F1, confusion matrix, and alert volume at the chosen threshold. Because only 3.33% of rows are positive, PR-AUC and precision at a fixed alert budget are the headline metrics, not accuracy. We will report against an explicit business baseline: flag any account whose 30-day active-user trend falls more than 25%.

A separate illustrative value model estimates protected ARR using clearly labelled assumptions: accounts alerted x mean `arr_usd` x expected save rate.

## Architecture / Tech Stack

The solution uses Microsoft Fabric as the data and intelligence foundation:

1. Source and ingestion: the 1.7 GB master CSV lands unchanged in OneLake Lakehouse Bronze. A notebook-based replayer streams the daily snapshots forward in simulated time as JSON events for the live demonstration, so the stream carries genuine day-over-day behaviour change rather than synthetic jitter.
2. Data preparation: Fabric notebooks using PySpark cast types, partition by `snapshot_date`, shred the denormalised master into conformed Silver entities (Account, Contact, Subscription, UsageDaily, Support, Interaction), and write Delta tables.
3. Customer 360 and machine learning: the Gold layer holds the account-day feature view, including trend features computed over the true history (7/30/90-day deltas, seat-utilisation ratio, days-to-renewal). A Fabric Data Science notebook trains a gradient-boosted churn classifier, tracks runs and metrics with MLflow, and scores the holdout.
4. Leakage control: the split is both out-of-time and out-of-account. Training uses earlier snapshot dates for one set of accounts; evaluation uses later dates for accounts the model has never seen. Post-cancellation rows do not exist in the data, and no feature is derived from the label.
5. Explainability: the scored account view stores risk level, top business-readable drivers, and recommended play, using SHAP values mapped to plain-language reasons such as "seat utilisation down 37% over 30 days" or "2 critical tickets open, resolution time tripled".
6. Real-time path: Eventstream receives the replayed events and routes them to Eventhouse. KQL serves the longitudinal view — rolling usage trends, ticket bursts, and the latest risk state per account.
7. Activation: Activator evaluates the risk threshold. When an account crosses it, Activator creates a retention alert or CRM task containing the account, ARR, score, drivers, and recommended play.
8. Consumption: Power BI over the Gold risk table provides the portfolio dashboard, the ranked retention workbench, and the Customer 360 account page with its 2-year behavioural history.
9. Enterprise controls: medallion boundaries, Delta tables, MLflow tracking, lineage, least-privilege access, and a seeded, re-runnable generator that makes the entire dataset reproducible from source.

The initial release prioritizes a reliable batch score-to-action path. Eventstream, Eventhouse, and Activator complete the near-real-time demonstration. Copilot or Fabric Data Agent Q&A is a stretch capability and is not required for the core outcome.

## Demo outcome

We replay a real account's final months. Its seat utilisation and API usage decay, critical tickets open, resolution times stretch, and the CSM touch gap widens. The churn probability climbs across the replayed days and crosses the configured threshold roughly 90 days before the actual cancel date held in the data. The system displays the risk level, the top drivers, and a recommended retention play, and the alert reaches the customer success team in the same workflow. Because the true `churn_date` is known, we can show on screen that the warning arrived in time.

## Recommended evidence to attach

- Architecture diagram: `submission/Customer_Intelligence_Engine_Architecture.svg`
- Dataset generator: `generate_master_csv.py` (seeded and reproducible)
- Dataset profile: row counts, churn rate, label balance, and the pre-churn signal separation table
- Notebook screenshots: ingestion, MLflow metrics, SHAP drivers, and scored accounts
- Power BI dashboard screenshot or export
- Short demo video showing the lead-time-to-alert flow against a known `churn_date`
