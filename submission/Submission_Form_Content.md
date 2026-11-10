# Customer Intelligence Engine

## Idea

**Customer Intelligence Engine: Explainable Churn Signals to Retention Action**

## Industry and customer problem

B2B SaaS customer-success teams need to identify accounts that may churn, understand the signals behind a risk score, and prioritise a useful review before renewal. Product usage, support activity, and customer-success interaction indicators are often reviewed separately.

This project demonstrates an account-day feature view, a probability of churn within the next 90 days, signed model contributions, and a human-reviewed retention task. It is designed to answer: which accounts should we review, what evidence influenced the score, and what action should a person consider? This is not a Fabric IQ ontology or a multi-source identity-resolution system.

## Data foundation

The demo uses a seeded, purpose-built **synthetic** B2B SaaS dataset. It has 10,000 accounts, a 730-day date window (2024-01-01 to 2025-12-30), 41 source columns, and 6,669,117 observed account-days. The generator intentionally injects degradation 60-120 days before some synthetic churn dates. Those constructed signals support a repeatable technical demonstration, not proof of real-world customer behavior.

| Property | Value |
|---|---:|
| Accounts | 10,000 |
| Churned accounts | 2,471 (24.7%) |
| Raw positive `label_churn_next_90d` rows | 222,390 (3.33%) |
| Source rows | 6,669,117 |
| Gold tables | Account-day features and separate training outcomes |

Known caveats: subscription/account dates are inconsistent for many rows; support/contact rolling measures are approximate; tenant IDs are effectively one-per-account; churned accounts stop after cancellation-day rows. Cancellation-day records are excluded from the at-risk population. Future outcome and cancellation fields are excluded from model predictors and operational report views. Refer to [the project memory](../PROJECT_MEMORY.md) for counts, eligibility rules, and validation details.

## Demonstrated implementation

1. **Data engineering:** CSV upload to OneLake Lakehouse; Bronze, seven typed Silver entity tables, and Gold account-day features/outcomes built with Fabric Spark.
2. **Customer 360:** Gold account-day feature table assembled using generated stable IDs. This is a one-source conformed view, not entity resolution; no match-quality report or Fabric IQ ontology was built.
3. **ML:** account/time-disjoint split; 13 allowlisted features; training-only median imputation; regularised Spark Logistic Regression. The saved pipeline is `Files/models/churn_lr_v1`; Fabric ML registry registration is not evidenced.
4. **Evaluation:** untouched test cohort of 1,679 accounts / 21,178 Monday snapshots. At High threshold 0.05, TP/FP/FN/TN = 925/10/211/20,032. Precision 98.93%, recall 81.43%, F1 89.33%, Spark `areaUnderPR` 0.8997. Derived accuracy 98.96%; always-negative accuracy is 94.64%. Derived precision lift over 5.36% test prevalence is 18.44x. Row-level observations are correlated; unique-account detection was 152 of 179 accounts (84.92%).
5. **Explainability:** full signed coefficient contributions relative to training medians reconstruct every score. These are not SHAP values and do not establish causality.
6. **Reporting:** three-page Power BI report—Portfolio Overview, Account History, Retention Actions. On September 30, 2025, 1,582 of 7,982 eligible accounts were scored (19.82% cohort coverage): 55 High, 5 Medium, 1,522 Low. Direct Lake mode is unverified.
7. **Event/action:** seven saved historical risk-score events flowed through Eventstream into Eventhouse. An event-level Activator rule invoked a validating notebook handler and created a retention task. This is not raw live usage ingestion or live model inference. Email/Teams/CRM delivery was not demonstrated; notification status was “Not attempted.”
8. **Segmentation:** displayed segment is a rule-based strongest-contributor category in scored history. Scheduled refresh and a versioned segment-membership audit are not evidenced.

### Warning-time interpretation

In the held-out synthetic test, the 152 detected accounts had a median first-correct-alert lead of 54 days (minimum 3, maximum 90), measured within the test period. It is not a guarantee of 90 days' warning, not a lifetime-first alert measure, and not an observed customer outcome.

## Business value and proposed extension

The current proof prioritises reviews and proposes human-reviewed plays; it does not measure saved revenue, customer adoption, intervention effect, or time saved. `ARR * score` is an uncalibrated prioritisation proxy, not expected loss.

**Business analyst suggestion—future AI-assisted capability, not implemented:** based on a risk profile and its evidence, an AI assistant could propose tailored retention-marketing strategies from a governed, approved playbook. For example:

- Usage/adoption decline -> offer a role-specific onboarding or feature-adoption session.
- Support friction -> propose a service-recovery conversation and coordinated support follow-up, not a generic discount.
- Low customer-success engagement -> draft a value-review/check-in campaign for the account owner.

Each proposal should explain the triggering signals, intended audience, assumptions, suggested channel and success measure; respect consent, contact preferences, suppression rules, and campaign eligibility; and require CSM/marketing approval. Do not autonomously send outreach. Test incremental retention against an appropriate control before claiming campaign uplift or ROI.

A future grounded Customer Intelligence Copilot could answer supported portfolio questions and draft these proposals using approved playbooks, governed read-only metrics, citations, caller permissions, and abstention on missing evidence. Copilot Studio/Fabric Data Agent, Fabric IQ, and this strategy-generation function are future concepts, not delivered features.

## Judges' evidence and boundaries

The supplied judging rubric allocates Business Value 25, Technical Excellence 20, Solution Quality 25, Innovation 15, and Presentation & demo 15. The credible differentiator is the verified score -> historical score event -> Activator -> persisted human-review task loop, paired with a time/account-disjoint test and reconstructable signed explanations.

The demo should lead with the business problem, show the held-out result with the high majority-class accuracy baseline disclosed, show report date/coverage, and finish with the persisted task. Clearly state synthetic data, limited scored cohort, historical score replay, no notification, and no chatbot. The detailed feature audit and 5-10 minute rehearsal checklist are in [Judges_Readiness_and_Gap_Review.md](./Judges_Readiness_and_Gap_Review.md).

## Architecture

The [architecture diagram](./Customer_Intelligence_Engine_Architecture.svg) shows the implemented Lakehouse/model/report/replay/action path. Fabric IQ ontology, real multi-source identity resolution, Eventhouse KQL behavioral journeys, scheduled auditable segmentation, model-registry registration, Copilot Studio, Purview labels, Direct Lake mode, and delivered notifications are not evidenced. Use the gap review for future work and verification criteria.
