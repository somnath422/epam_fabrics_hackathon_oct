# Ashish: data engineering and Customer 360

[Handbook](./README.md) | [Daily board](./01_Day_by_Day_Plan.md) | [Contracts](./02_Shared_Contracts_and_Acceptance.md)

You are Developer 1. Your consumers are Irfan (features/outcomes), Lokesh (metadata/history), and Somnath (orchestration). You own `01_ingest_validate` and `02_silver_gold`.

## Before starting

- Somnath has created the workspace and Lakehouse and granted named access.
- Use Fabric browser notebooks with **PySpark / Python** cells.
- Attach `lh_customer_intelligence` as the default Lakehouse.
- Python cells below are notebook code, not PowerShell.
- Do not collect the complete source into pandas.
- These are build instructions and starter cells; execute and validate them in Fabric before declaring success.

## October 29: source and Bronze

### D01: inspect the local input

Use the [CSV](../output/master_saas_b2b_daily_10k_2y_2024.csv), not the archived telco file. Confirm OneDrive has downloaded it locally. Keep the original unchanged.

Expected: 41 columns, 6,669,117 rows, 10,000 accounts, dates January 1, 2024-December 30, 2025.

### D02: upload

1. Fabric workspace -> open Lakehouse.
2. Files -> create folder `bronze`.
3. Open folder -> Upload -> Upload files.
4. Choose the CSV; wait until upload completes.
5. Confirm exact filename.

If repeated upload failures or size restrictions occur, split locally into smaller header-preserving CSV parts. Example Python, saved as a separate helper and run in Python:

```python
from pathlib import Path
import pandas as pd

source = Path("output/master_saas_b2b_daily_10k_2y_2024.csv")
destination = Path("output/master_parts")
destination.mkdir(exist_ok=True)
if any(destination.iterdir()):
    raise RuntimeError("Use an empty parts directory to avoid stale files")

for index, chunk in enumerate(
    pd.read_csv(source, dtype=str, keep_default_na=False, chunksize=100_000)
):
    chunk.to_csv(destination / f"part-{index:04d}.csv", index=False)
```

Upload only those parts into `Files/bronze/master_parts`. Do not mix the original and parts under a wildcard read.

### D03: create `01_ingest_validate`

Notebook cell:

```python
from pyspark.sql import functions as F

SOURCE = "Files/bronze/master_saas_b2b_daily_10k_2y_2024.csv"
# If split: use "Files/bronze/master_parts/*.csv" instead.
raw = (
    spark.read.option("header", True)
    .option("inferSchema", False)
    .option("mode", "FAILFAST")
    .csv(SOURCE)
)
assert len(raw.columns) == 41

profile = raw.agg(
    F.count("*").alias("rows"),
    F.countDistinct("account_id").alias("accounts"),
    F.min("snapshot_date").alias("start"),
    F.max("snapshot_date").alias("end"),
).first()
print(profile.asDict())
assert profile["rows"] == 6_669_117
assert profile["accounts"] == 10_000
assert profile["start"] == "2024-01-01"
assert profile["end"] == "2025-12-30"

missing_keys = raw.filter(
    F.col("account_id").isNull()
    | (F.trim("account_id") == "")
    | F.col("tenant_id").isNull()
    | (F.trim("tenant_id") == "")
    | F.col("snapshot_date").isNull()
)
assert missing_keys.limit(1).count() == 0
assert (
    raw.groupBy("tenant_id", "account_id", "snapshot_date")
    .count().filter("count > 1").limit(1).count()
) == 0

(
    raw.withColumn("_source_file", F.input_file_name())
    .withColumn("_ingested_at", F.current_timestamp())
    .write.format("delta").mode("errorifexists")
    .saveAsTable("bronze_master_daily")
)
```

`errorifexists` prevents accidental replacement. If rerunning after successful creation, read the existing table and revalidate it; do not casually switch to overwrite.

## October 30: typed Silver and features

### D04: create `02_silver_gold`

Use explicit numeric/date casts. Preserve raw Bronze for auditing.

```python
from pyspark.sql import functions as F, Window

bronze = spark.table("bronze_master_daily")
date_fields = [
    "snapshot_date", "created_date", "primary_contact_created_date",
    "subscription_start_date", "renewal_date", "cancel_date", "churn_date",
]
integer_fields = [
    "employee_count", "seats_purchased", "active_users", "sessions",
    "feature_a_events", "feature_b_events", "feature_c_events",
    "api_calls", "licensed_seats", "tickets_created_today",
    "tickets_closed_today", "critical_open_tickets",
    "tickets_created_30d", "interactions_30d",
    "days_since_last_csm_touch", "will_churn",
    "label_churn_next_90d", "days_to_churn",
]
double_fields = [
    "arr_usd", "mrr_usd", "avg_ttr_days_60d", "no_show_rate_90d",
]
types = (
    {name: "date" for name in date_fields}
    | {name: "bigint" for name in integer_fields}
    | {name: "double" for name in double_fields}
)
typed = bronze.select(*[
    F.expr(f"try_cast(`{name}` as {types[name]})").alias(name)
    if name in types else F.col(name)
    for name in bronze.columns
])

# A nonempty source value becoming null is a conversion error.
for name in types:
    bad = bronze.filter(
        F.col(name).isNotNull()
        & (F.trim(F.col(name)) != "")
        & F.expr(f"try_cast(`{name}` as {types[name]})").isNull()
    )
    assert bad.limit(1).count() == 0, f"Invalid {name}"

assert typed.filter("snapshot_date IS NULL").limit(1).count() == 0
assert typed.filter(
    "label_churn_next_90d IS NULL OR label_churn_next_90d NOT IN (0, 1)"
).limit(1).count() == 0
```

The loop is easy to understand but scans repeatedly. Once correctness is established, combine checks into one aggregation if runtime is a measured problem.

### D05: validate business relationships

At minimum check:

- Counts and revenue nonnegative, except `days_to_churn=-1` sentinel for nonchurners.
- `active_users <= licensed_seats`.
- `no_show_rate_90d` between zero and one.
- Daily sequence has no missing dates per account before cancellation.
- `will_churn=1` implies valid churn date.
- Churner `days_to_churn = datediff(churn_date, snapshot_date)`.
- Label is one exactly when `0 < days_to_churn <= 90`.
- No snapshots after known cancellation.
- Created date <= contact created date; subscription/date validity separately flagged.

The generator includes cancellation-day snapshots and future outcome fields. They are valid for evaluation storage, not model input.

Persist failed-row counts and a small sample to an isolated quality table; fail the run for broken keys/outcomes. For invalid subscription timelines, flag and exclude subscription-derived features until Somnath/Archi approve a policy. Do not repair by inventing dates.

Create separate Silver surfaces:

| Table | Grain/content |
|---|---|
| `silver_account` | Distinct tenant/account and static metadata; assert uniqueness |
| `silver_contact` | Contact ID, account key, role, created date |
| `silver_subscription_daily` | Subscription/account/date and status/context; restricted where outcomes leak |
| `silver_usage_daily` | Account/date usage counts |
| `silver_support_daily` | Account/date approximate support signals |
| `silver_interaction_daily` | Account/date approximate interaction signals |

Use `select(...).distinct()` only for verified static dimensions. It is not a substitute for resolving conflicting values.

### D06: build historical features

Starter calendar-window cells:

```python
base = typed.withColumn(
    "_day", F.datediff("snapshot_date", F.lit("1970-01-01"))
)
ordered = Window.partitionBy("tenant_id", "account_id").orderBy("_day")
recent7 = ordered.rangeBetween(-6, 0)
recent30 = ordered.rangeBetween(-29, 0)
prior30 = ordered.rangeBetween(-59, -30)
past = ordered.rangeBetween(Window.unboundedPreceding, 0)

features = (
    base
    .withColumn("active_users_avg_7d", F.avg("active_users").over(recent7))
    .withColumn("active_users_avg_30d", F.avg("active_users").over(recent30))
    .withColumn("_users_prior", F.avg("active_users").over(prior30))
    .withColumn("_api_recent", F.avg("api_calls").over(recent30))
    .withColumn("_api_prior", F.avg("api_calls").over(prior30))
    .withColumn("history_days_available", F.count("*").over(past))
    .withColumn(
        "seat_utilisation",
        F.when(F.col("licensed_seats") > 0,
               F.col("active_users") / F.col("licensed_seats"))
    )
    .withColumn(
        "usage_change_30d",
        F.when(F.col("_users_prior") > 0,
               F.col("active_users_avg_30d") / F.col("_users_prior") - 1)
    )
    .withColumn(
        "api_change_30d",
        F.when(F.col("_api_prior") > 0,
               F.col("_api_recent") / F.col("_api_prior") - 1)
    )
    .withColumn("feature_ready", F.col("history_days_available") >= 60)
    .withColumn(
        "subscription_dates_valid",
        (F.col("created_date") <= F.col("subscription_start_date"))
        & (F.col("subscription_start_date") <= F.col("snapshot_date"))
        & (F.col("renewal_date") > F.col("snapshot_date"))
    )
)
```

`feature_ready` also requires the critical quality checks above to pass. If daily gaps are found, do not treat 60 arbitrary observations as 60 complete days.

Drop future-outcome fields and temporary window fields before writing Gold:

```python
keys = ["tenant_id", "account_id", "snapshot_date"]
outcomes = typed.select(
    *keys, "will_churn", "churn_date", "cancel_date",
    "label_churn_next_90d", "days_to_churn"
).withColumn(
    "at_risk_population",
    F.col("churn_date").isNull()
    | (F.col("snapshot_date") < F.col("churn_date"))
)

forbidden = [
    "will_churn", "churn_date", "cancel_date", "days_to_churn",
    "label_churn_next_90d", "subscription_status",
]
temporary = ["_day", "_users_prior", "_api_recent", "_api_prior"]
gold = features.drop(*(forbidden + temporary))

gold.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_customer360_daily"
)
outcomes.write.format("delta").mode("errorifexists").saveAsTable(
    "gold_training_outcomes"
)
```

Avoid 730 daily partitions for a 1.7 GB input. Start unpartitioned and use the runtime's optimized defaults. Revisit only when measured query behavior warrants it.

## October 31: publish and hand off

### D07

Send Irfan:

- Gold schema, quality output, feature formulas, source version.
- Outcome table and `at_risk_population` definition.
- Small real extract and account split key definition.
- Invalid-date exclusions.

Send Lokesh metadata field names and a bounded history extract. Do not send outcome fields to operational report tables.

Derived tables need a rerun policy. Prefer a versioned staging table and publish after validation. If using overwrite for an exclusively owned derived table, obtain agreement and avoid concurrent consumers during replacement.

## November 1: temporal tests

### D08

Choose a small deterministic account set and date t:

1. Compute features from full history.
2. Filter source to dates <= t and recompute.
3. Compare features at t within numeric tolerance.
4. They must match.
5. Check first 59 days are not feature-ready.
6. Check zero baseline produces null change, not infinity or fictitious zero.
7. Check weekend effects are not mistaken for 30-day decline by a single-day comparison.

## November 2: replay extract

- D09: give Sujith a bounded approved account/date cohort, ordered and with actual feature timestamps.

## November 3: negative tests

- D10: in isolated fixtures, test duplicate keys, invalid date, negative count, missing source, and post-cancel row. Each must produce a visible quality result.
- Never edit accepted source data for these tests.

## November 4: freeze

- D11: freeze schema and feature definitions; record source/table versions.

## November 5: export and reload

- D12: export notebooks, dictionary, DQ outputs, source manifest, and reload instructions.
- Verify the exported notebook and source references can be opened from approved storage.

## November 6: submission support

- Support final smoke test without regenerating or silently replacing the accepted dataset.

## Troubleshooting

| Symptom | Action |
|---|---|
| Path missing | Check default Lakehouse and exact Files path |
| Existing table error | Reuse/validate table; do not blindly overwrite |
| Spark unavailable/throttled | Coordinate with Somnath; stop competing sessions; do not resize |
| Unexpected nulls after cast | Inspect original Bronze values and record conversion errors |
| Driver memory failure | Remove pandas/collect on full data; reduce only the bounded extract |
| Duplicate account dimension | Investigate conflicting static values; do not select an arbitrary first row |
