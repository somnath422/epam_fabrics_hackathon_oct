# Irfan: ML, evaluation, scoring, and explanations

[Handbook](./README.md) | [Daily board](./01_Day_by_Day_Plan.md) | [Contracts](./02_Shared_Contracts_and_Acceptance.md)

You are Developer 2. Own `03_train_evaluate`, `04_score_explain`, model artifacts, metric tables, and model-generated risk outputs. Coordinate compute with Somnath.

## October 29: lock the experiment design

### M01: define population and allowlist

Predict cancellation within 90 days for accounts not yet cancelled at snapshot time, with enough historical observations. Cancellation-day records are excluded, even though their label is zero.

Suggested v1 numeric features:

```python
FEATURES = [
    "seat_utilisation",
    "active_users_avg_7d",
    "active_users_avg_30d",
    "usage_change_30d",
    "api_change_30d",
    "critical_open_tickets",
    "tickets_created_30d",
    "avg_ttr_days_60d",
    "interactions_30d",
    "days_since_last_csm_touch",
    "no_show_rate_90d",
]
FORBIDDEN = {
    "will_churn", "churn_date", "cancel_date", "days_to_churn",
    "label_churn_next_90d", "subscription_status",
    "account_id", "tenant_id", "primary_contact_id", "subscription_id",
}
assert not (set(FEATURES) & FORBIDDEN)
```

Do not use all numeric fields automatically. Subscription-derived time features remain excluded until source chronology is validated.

### M02: split by account and time

Deterministic account assignment in Spark:

```python
from pyspark.sql import functions as F

features = spark.table("gold_customer360_daily")
outcomes = spark.table("gold_training_outcomes")
keys = ["tenant_id", "account_id", "snapshot_date"]
dataset = (
    features.join(outcomes, keys, "inner")
    .filter("feature_ready AND at_risk_population")
    .withColumn(
        "_bucket",
        F.pmod(F.xxhash64("tenant_id", "account_id"), F.lit(10))
    )
)
train = dataset.filter(
    (F.col("_bucket") < 6)
    & (F.col("snapshot_date") <= F.lit("2024-09-30").cast("date"))
)
validation = dataset.filter(
    F.col("_bucket").between(6, 7)
    & F.col("snapshot_date").between("2025-01-01", "2025-03-31")
)
test = dataset.filter(
    (F.col("_bucket") >= 8)
    & F.col("snapshot_date").between("2025-07-01", "2025-09-30")
)
```

Why these periods:

- Last training snapshot's 90-day outcome is observable before validation.
- Last validation snapshot's 90-day outcome is observable before test.
- Test follow-up through December 29 is within the source window.
- Held-out accounts may use their own earlier telemetry for trailing features, not model fitting.

Assert disjoint account sets. Report actual churner/positive counts and prevalence for each subset; they differ from the full dataset's 3.33%.

## October 30: bounded training and baselines

### M03: extract without exhausting memory

1. Spark handles the complete history.
2. For training, use a reproducible snapshot cadence, such as every seventh day, and then a bounded sample.
3. Print planned row counts and estimated memory before `toPandas()`.
4. Start with <=100,000 numeric training rows.
5. Keep validation/test evaluation representative; do not balance them by target.
6. Use full daily ordered trajectories for lead-time evaluation on the declared cohort, not a random row sample.
7. If training is balanced/weighted, retain natural validation/test prevalence and assess calibration.

Example deterministic weekly cadence:

```python
weekly_train = train.filter(
    F.pmod(
        F.datediff("snapshot_date", F.lit("2024-01-01")),
        F.lit(7)
    ) == 0
)
training_extract = weekly_train.orderBy(
    F.xxhash64("tenant_id", "account_id", "snapshot_date")
).limit(100_000)
pdf_train = training_extract.select(
    *FEATURES, "label_churn_next_90d"
).toPandas()
assert pdf_train["label_churn_next_90d"].nunique() == 2
```

This bounds training, not the declared evaluation cohort. Save the extraction rule and row manifest for reproducibility.

### M04: fit simple baselines

Rule baseline: `usage_change_30d <= -0.25`. Missing trends require an explicit abstention/missing-data policy, not silent "healthy" classification.

Starter scikit-learn training:

```python
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier

X_train = pdf_train[FEATURES]
y_train = pdf_train["label_churn_next_90d"].astype(int)

linear = make_pipeline(
    SimpleImputer(strategy="median", add_indicator=True),
    StandardScaler(),
    LogisticRegression(max_iter=1000, random_state=42),
)
boosted = make_pipeline(
    SimpleImputer(strategy="median"),
    GradientBoostingClassifier(
        n_estimators=100, max_depth=3, random_state=42
    ),
)
linear.fit(X_train, y_train)
boosted.fit(X_train, y_train)
```

Require at least one nonnull training value per feature before fitting. Fit all preprocessing on training only. Start with installed runtime packages; install missing dependencies only after an import failure or dependency change.

### M05: MLflow

1. Create/select experiment `exp_customer_churn`.
2. Start a named run per candidate.
3. Log source/feature versions, split/extraction rules, seed, feature list, and model parameters.
4. Log validation metrics and counts.
5. Log the complete fitted preprocessing+model pipeline with an input example/signature using the installed MLflow API.
6. Save the selected model run URI; a notebook variable is not a persisted model.
7. Reload the persisted model and compare predictions before publication.

Use the installed MLflow API version; do not copy credentials or invent registry permissions.

## October 31: score the first real slice

### M06

1. Select one permitted reporting date and a bounded real account cohort.
2. Load the saved pipeline.
3. Preserve tenant/account/date keys outside the feature matrix.
4. Compute positive-class probability with `predict_proba`.
5. Assert every score is finite and between zero and one.
6. Add model version, current scoring UTC timestamp, feature as-of date, run ID, and `is_fixture=false`.
7. Persist `gold_account_risk`.
8. Pair with Somnath to publish the reporting table.
9. Give Lokesh actual scores immediately; do not wait for final polish.

## November 1: threshold, test, explanations

### M07: choose threshold on validation only

With Archi:

1. Agree a weekly top-K account budget and minimum acceptable precision if any.
2. Evaluate candidate thresholds using validation data only.
3. Report resulting alerts per period, precision, and recall.
4. Freeze High and Medium boundaries and record them in release config.
5. If top-K ranking and fixed-threshold alerts are both used, explain they are separate policies.

Do not select K from test outcomes. If no threshold meets the business assumption, report that rather than falsifying a success target.

### M08: evaluate the locked choice

On the identical held-out population compare:

- Rule baseline.
- Logistic regression.
- Selected boosted classifier.

Use average precision explicitly if using `average_precision_score`; label it "Average precision (PR summary)" rather than silently mixing it with trapezoidal PR-AUC.

Report:

- Account-day counts and prevalence.
- Average precision, precision, recall, F1, confusion matrix.
- Precision@K and alert volume on one snapshot per account per scoring period.
- Account-level churn detection coverage.
- Median lead time among detected churners.
- Fraction of eligible churners detected >=30, >=60, >=90 days ahead.
- Fraction not detected.

If the test set is inspected for tuning, it is no longer untouched test data. Disclose revisions; do not quietly reuse it as proof.

### M09: SHAP and explanations

For the fitted boosted pipeline:

1. Import SHAP; if missing, add the dependency through the supported Fabric environment/session mechanism.
2. Transform the declared scoring feature matrix using the fitted training imputer.
3. Explain the tree estimator, not a separate newly fitted model.
4. Check the installed SHAP output shape. Binary classifiers/version combinations differ; identify the positive-class axis explicitly.
5. Rank contributions increasing churn risk, then attach actual as-of feature values.
6. Persist top drivers and contribution metadata.

Example for the scikit-learn GradientBoosting binary estimator:

```python
import numpy as np
import shap

imputer = boosted.steps[0][1]
tree = boosted.steps[-1][1]
transformed = imputer.transform(X_train.iloc[:100])
explainer = shap.TreeExplainer(tree)
explanation = explainer(transformed)
values = np.asarray(explanation.values)
assert values.shape == transformed.shape, (
    "Inspect class axes for this runtime before using driver values"
)
```

Explain a bounded reporting/replay cohort to control runtime. SHAP may be in raw log-odds for this model; never call a raw contribution a percentage-point probability change.

Reason template:

> "30-day active-user average changed by -31% versus the preceding 30 days; this feature increased the model's risk estimate."

Only produce the percentage from the actual feature value. A positive contribution does not prove a causal mechanism or an effective intervention.

If SHAP is unavailable, use transparent observed-signal reasons and label them as rules, not SHAP. Update the presentation.

## November 2: replay and account-level lead time

### M10

1. Score each approved replay account's daily states in chronological order.
2. Include enough pre-alert history to show the transition.
3. Determine the first eligible alert under the frozen rule.
4. In evaluation-only data, join actual churn date.
5. Compute `lead_time_days = churn_date - first_alert_snapshot_date`.
6. Retain all eligible churners in the detection denominator, including undetected ones.
7. Mark accounts whose first observed alert is at the evaluation-window boundary; true first warning may precede the window.
8. Give Sujith the bounded scored events with model version and real drivers.

Do not expose outcomes in the operational account report. Put the lead-time reveal in an explicitly labeled evaluation page or screenshot.

## November 3: robustness and calibration

### M11

- Missing required feature -> explicit failure, not all-zero scoring.
- Unexpected model/feature version -> failure.
- Missing/invalid probability -> failure.
- Account/time split overlap -> failure.
- Date beyond complete outcome follow-up -> censored/excluded evaluation row.
- Calibration: inspect reliability/Brier score on representative held-out data; do not fit calibration on test.
- Synthetic data may be exceptionally easy. Report that instead of claiming production-ready accuracy.

If calibration is weak, label ARR multiplication a ranking proxy. Do not improve the financial story by relabeling probabilities.

## November 4: freeze

- M12: freeze feature list, model, thresholds, extract manifests, and evaluation scope.

## November 5: export and reproduce

- M13: reload from exported artifact and reproduce saved predictions within agreed numerical tolerance.
- Export model card: purpose, source, population, exclusions, split, metrics, lead times, synthetic limits, intended use, and prohibited claims.

## November 6: submission support

- Support final smoke test; no last-day tuning.

## Handoff checklist

- [ ] Ashish's feature contract acknowledged.
- [ ] Persisted model can reload.
- [ ] Operational outputs contain no future outcomes.
- [ ] Lokesh receives risk/history tables for one release.
- [ ] Sujith receives flat ordered scored events.
- [ ] Archi receives cohort-wide metrics, not just a success account.
- [ ] Somnath receives model URI, thresholds, run ID, and known limits.
