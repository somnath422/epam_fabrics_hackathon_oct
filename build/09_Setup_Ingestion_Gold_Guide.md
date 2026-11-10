# Step-by-step: resources, ingestion, and Gold dataset

[Handbook](./README.md) | [Contracts](./02_Shared_Contracts_and_Acceptance.md) | [Ashish runbook](./05_Ashish_Data_Engineering.md)

Use this guide to create the Fabric workspace and Lakehouse, load the CSV, and build the Gold Customer 360 dataset.

**Your sandbox already provides `capacity2447013`. Do not create another Fabric capacity.**

The notebook code is written for Fabric Spark notebooks. The data-foundation build and its checks were subsequently completed in the sandbox; see the [current handoff](../PROJECT_MEMORY.md) for recorded results and limitations. A new environment must rerun the cells in order and stop at the first failed check.

---

## Part 0: protect the sandbox credentials

- Don't paste the username and Temporary Access Pass (TAP) into chat, documents, notebooks, or screenshots.
- Treat a TAP that has already been shared as exposed. If it went beyond your trusted team, ask CloudLabs support to reset it.
- Don't let six people share one login. Ask support whether teammates can get their own identities or workspace access.
- Never put a credential in notebook code.

---

## Part 1: sign in and check the capacity

1. Open a private/incognito browser window.
2. Go to `https://portal.azure.com`.
3. Enter the sandbox username, then the Temporary Access Pass.
4. Complete any security setup prompts (e.g. password or Microsoft Authenticator registration).
5. In the top search bar, type **Microsoft Fabric** and open it.
6. Open **`capacity2447013`**.
7. Write down the **SKU**, **Region**, and **Status**.
8. If the status is **Paused**, select **Resume** and wait until it shows **Active**.

| You see | Do this |
|---|---|
| Capacity not listed | Check you are in the sandbox directory (profile icon → Switch directory), then contact support |
| SKU is not F2 | Don't resize it; just note it |
| "No access" errors | Contact support with the exact error and UTC time; don't send the password |

---

## Part 2: create the workspace

1. Open `https://app.fabric.microsoft.com` in the same private window.
2. Confirm the profile icon (top right) shows the sandbox user.
3. Left menu → **Workspaces** → **+ New workspace**.
4. **Name:** `ws_customer_intelligence`.
5. Expand **Advanced**.
6. **License mode:** **Fabric capacity**.
7. **Capacity:** **`capacity2447013`**.
8. Select **Apply**.

**Check:** In the workspace, select **+ New item**. You should see **Lakehouse**, **Notebook**, and **Eventstream**. If you only see Power BI items, the capacity isn't assigned: open **Workspace settings → License info**, choose `capacity2447013`, and save.

**Teammates (optional):** Workspace → **Manage access** → **Add people or groups**, only for identities support has approved. Give developers **Contributor** and Archi **Viewer**.

---

## Part 3: create the Lakehouse

1. Workspace → **+ New item** → **Lakehouse**.
2. **Name:** `lh_customer_intelligence`.
3. Leave the **Lakehouse schemas** option at its default.
4. Select **Create**.

You should see two sections: **Tables** and **Files**.

**If schemas are enabled**, tables appear under `dbo`. The notebook code below still works with plain table names.

---

## Part 4: upload the CSV

Local file: [master_saas_b2b_daily_10k_2y_2024.csv](../output/master_saas_b2b_daily_10k_2y_2024.csv) (about 1.7 GiB). This generated file is not committed; regenerate it using the [handoff instructions](../PROJECT_MEMORY.md#7-local-setup-and-safe-replay).

**Existing sandbox:** the completed upload is at `Files/master_saas_b2b_daily_10k_2y_2024.csv`, directly under Files. Use that path when resuming. The `bronze` subfolder below is an optional layout for new uploads; match Notebook 1's source path to the layout actually used.

1. In Finder, right-click the file → **Always Keep on This Device**. Wait until OneDrive finishes downloading it.
2. In the Lakehouse, hover over **Files** → **…** → **New subfolder** → `bronze`.
3. Open `bronze` → **Upload** → **Upload files**.
4. Select the CSV → **Upload**.
5. Keep the browser tab open until upload finishes.
6. Refresh `bronze` and confirm the file and its size.

### If the upload fails or stalls

Split the file into roughly 125 MB parts, each with the header. Run this in the macOS **Terminal** (not a notebook):

```bash
cd "/Users/Somnath_Roy/Library/CloudStorage/OneDrive-EPAM/Hackathon/Fabrics Hackathon oct 26/output"
mkdir master_parts
tail -n +2 master_saas_b2b_daily_10k_2y_2024.csv | split -l 500000 - master_parts/part_
for f in master_parts/part_*; do
  { head -n 1 master_saas_b2b_daily_10k_2y_2024.csv; cat "$f"; } > "$f.csv"
  rm "$f"
done
ls -lh master_parts
```

You should get 14 `.csv` files. Then:

1. In the Lakehouse, create the subfolder `Files/bronze/master_parts`.
2. Upload all 14 files into that folder.
3. Use the split-file path in Notebook 1 (below).
4. Don't put the full CSV in `master_parts`.

Delete the local `master_parts` folder once Bronze is validated so OneDrive doesn't sync an extra 1.8 GB.

---

## Part 5: how to use notebooks

For each notebook below:

1. Workspace → **+ New item** → **Notebook**.
2. Rename it (top-left name).
3. In the left **Explorer**, select **Add data items** → **Existing data sources** → `lh_customer_intelligence` → **Add**. (In some versions this is **+ Lakehouses** → **Existing lakehouse**.)
4. Confirm the language is **PySpark (Python)**.
5. Paste each cell into its own code cell. Run with **Shift+Enter**.
6. Wait for each cell to finish before running the next.
7. When finished, select **Stop session** in the toolbar.

The first cell can take a few minutes while Spark starts. On a small capacity, run one notebook at a time.

---

## Part 6: Notebook 1 — `nb_01_ingest_bronze`

### Cell 1: read the CSV

```python
from pyspark.sql import functions as F

SOURCE = "Files/bronze/master_saas_b2b_daily_10k_2y_2024.csv"
# Using split files instead? Use this line:
# SOURCE = "Files/bronze/master_parts/*.csv"

raw = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .option("mode", "FAILFAST")
    .csv(SOURCE)
)

print("Columns:", len(raw.columns))
raw.show(3, truncate=False)
```

**Expected:** `Columns: 41`.

### Cell 2: validate the source profile

```python
profile = raw.agg(
    F.count("*").alias("rows"),
    F.countDistinct("account_id").alias("accounts"),
    F.min("snapshot_date").alias("first_date"),
    F.max("snapshot_date").alias("last_date"),
).first().asDict()
print(profile)

assert len(raw.columns) == 41, "Expected 41 columns"
assert profile["rows"] == 6_669_117, "Unexpected row count"
assert profile["accounts"] == 10_000, "Unexpected account count"
assert profile["first_date"] == "2024-01-01"
assert profile["last_date"] == "2025-12-30"

missing_keys = raw.filter(
    F.col("tenant_id").isNull() | (F.trim(F.col("tenant_id")) == "")
    | F.col("account_id").isNull() | (F.trim(F.col("account_id")) == "")
    | F.col("snapshot_date").isNull()
).count()
duplicate_keys = (
    raw.groupBy("tenant_id", "account_id", "snapshot_date")
    .count().filter("count > 1").count()
)
print("Missing keys:", missing_keys, "| Duplicate keys:", duplicate_keys)
assert missing_keys == 0 and duplicate_keys == 0

raw.groupBy("label_churn_next_90d").count().orderBy("label_churn_next_90d").show()
```

**Expected label counts:** `0 = 6,446,727` and `1 = 222,390`.

If an assertion fails, stop and report the printed values. Don't edit the expected numbers to make it pass.

### Cell 3: save Bronze

```python
(
    raw
    .withColumn("_source_file", F.input_file_name())
    .withColumn("_ingested_at", F.current_timestamp())
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("bronze_master_daily")
)

bronze_rows = spark.table("bronze_master_daily").count()
print(f"bronze_master_daily rows: {bronze_rows:,}")
assert bronze_rows == 6_669_117
```

Overwrite is safe here because Bronze can always be rebuilt from the uploaded file.

**Check:** Refresh **Tables** in the Lakehouse; `bronze_master_daily` should appear. Then **Stop session**.

---

## Part 7: Notebook 2 — `nb_02_silver`

### Cell 1: convert text columns to proper types

```python
from pyspark.sql import functions as F

bronze = spark.table("bronze_master_daily")

TYPES = {
    "snapshot_date": "date", "created_date": "date",
    "primary_contact_created_date": "date",
    "subscription_start_date": "date", "renewal_date": "date",
    "cancel_date": "date", "churn_date": "date",
    "employee_count": "int", "seats_purchased": "int",
    "active_users": "int", "sessions": "int",
    "feature_a_events": "int", "feature_b_events": "int",
    "feature_c_events": "int", "api_calls": "bigint",
    "licensed_seats": "int", "tickets_created_today": "int",
    "tickets_closed_today": "int", "critical_open_tickets": "int",
    "tickets_created_30d": "int", "interactions_30d": "int",
    "days_since_last_csm_touch": "int", "will_churn": "int",
    "label_churn_next_90d": "int", "days_to_churn": "int",
    "arr_usd": "double", "mrr_usd": "double",
    "avg_ttr_days_60d": "double", "no_show_rate_90d": "double",
}

def converted(name):
    return F.expr(f"try_cast(`{name}` AS {TYPES[name]})")

# A non-empty source value that converts to null is a data error.
bad = bronze.select(*[
    F.sum(
        F.when(
            F.col(c).isNotNull() & (F.trim(F.col(c)) != "") & converted(c).isNull(),
            1,
        ).otherwise(0)
    ).alias(c)
    for c in TYPES
]).first().asDict()
bad = {column: count for column, count in bad.items() if count}
print("Conversion errors:", bad or "none")
assert not bad

typed = bronze.select(*[
    converted(c).alias(c) if c in TYPES else F.col(c)
    for c in bronze.columns
    if not c.startswith("_")
])
typed.printSchema()
```

### Cell 2: business-rule checks

```python
expected_label = F.when(
    (F.col("days_to_churn") > 0) & (F.col("days_to_churn") <= 90), 1
).otherwise(0)

def count_if(condition, name):
    return F.sum(F.when(condition, 1).otherwise(0)).alias(name)

checks = typed.select(
    count_if(F.col("active_users") > F.col("licensed_seats"), "users_above_seats"),
    count_if(F.col("arr_usd") < 0, "negative_arr"),
    count_if((F.col("no_show_rate_90d") < 0) | (F.col("no_show_rate_90d") > 1), "bad_no_show_rate"),
    count_if((F.col("will_churn") == 1) & F.col("churn_date").isNull(), "churner_without_date"),
    count_if(F.col("churn_date").isNotNull() & (F.col("snapshot_date") > F.col("churn_date")), "rows_after_churn"),
    count_if(
        F.col("churn_date").isNotNull()
        & (F.datediff("churn_date", "snapshot_date") != F.col("days_to_churn")),
        "wrong_days_to_churn",
    ),
    count_if(F.col("label_churn_next_90d") != expected_label, "wrong_label"),
).first().asDict()

# Reported, not blocking: synthetic subscription timelines are imperfect.
date_flags = typed.select(
    count_if(F.col("subscription_start_date") < F.col("created_date"), "subscription_before_account"),
    count_if(F.col("subscription_start_date") > F.col("snapshot_date"), "subscription_starts_later"),
    count_if(F.col("renewal_date") <= F.col("snapshot_date"), "renewal_not_in_future"),
).first().asDict()

gap_accounts = (
    typed.groupBy("tenant_id", "account_id")
    .agg(
        F.count("*").alias("rows"),
        F.min("snapshot_date").alias("first_date"),
        F.max("snapshot_date").alias("last_date"),
    )
    .filter(F.col("rows") != F.datediff("last_date", "first_date") + 1)
    .count()
)

print("Blocking checks:", checks)
print("Accounts with missing days:", gap_accounts)
print("Date warnings (not blocking):", date_flags)

assert all(value == 0 for value in checks.values()), "Blocking data-quality failure"
assert gap_accounts == 0, "Daily history has gaps"
```

**Expected:** All blocking checks are `0`. Some subscription-date warnings may be above zero; the Gold step flags those rows.

### Cell 3: write Silver entity tables

```python
KEYS = ["tenant_id", "account_id", "snapshot_date"]

def save(df, name):
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(name)
    print(f"{name}: {spark.table(name).count():,} rows")

account = typed.select(
    "tenant_id", "account_id", "account_name", "domain", "industry", "region",
    "employee_count", "created_date", "arr_usd", "csm_owner",
).distinct()
assert account.count() == 10_000, "Account attributes vary within an account"
save(account, "silver_account")

contact = typed.select(
    "primary_contact_id", "tenant_id", "account_id",
    "primary_contact_role", "primary_contact_created_date",
).distinct()
assert contact.count() == 10_000
save(contact, "silver_contact")

save(typed.select(
    *KEYS, "subscription_id", "plan_tier", "seats_purchased", "mrr_usd",
    "subscription_start_date", "renewal_date", "subscription_status", "cancel_date",
), "silver_subscription_daily")

save(typed.select(
    *KEYS, "active_users", "sessions", "feature_a_events", "feature_b_events",
    "feature_c_events", "api_calls", "licensed_seats",
), "silver_usage_daily")

save(typed.select(
    *KEYS, "tickets_created_today", "tickets_closed_today",
    "critical_open_tickets", "tickets_created_30d", "avg_ttr_days_60d",
), "silver_support_daily")

save(typed.select(
    *KEYS, "interactions_30d", "days_since_last_csm_touch", "no_show_rate_90d",
), "silver_interaction_daily")

save(typed.select(
    *KEYS, "will_churn", "churn_date", "label_churn_next_90d", "days_to_churn",
), "silver_churn_outcomes")
```

**Expected:** Two account-level tables of 10,000 rows and five daily tables of 6,669,117 rows each.

`silver_subscription_daily` contains `subscription_status` and `cancel_date`, which reveal the future. Those columns must never become model features.

**Stop session** when done.

---

## Part 8: Notebook 3 — `nb_03_gold`

### Cell 1: the feature-building function

```python
from pyspark.sql import functions as F, Window

KEYS = ["tenant_id", "account_id", "snapshot_date"]

def build_customer360(usage, support, interaction, subscription, account):
    base = (
        usage
        .join(support, KEYS, "left")
        .join(interaction, KEYS, "left")
        .join(
            subscription.select(
                *KEYS, "plan_tier", "seats_purchased", "mrr_usd",
                "subscription_start_date", "renewal_date",
            ),
            KEYS, "left",
        )
        .join(
            account.select(
                "tenant_id", "account_id", "account_name", "industry", "region",
                "employee_count", "created_date", "arr_usd", "csm_owner",
            ),
            ["tenant_id", "account_id"], "left",
        )
        .withColumn("_day", F.datediff("snapshot_date", F.lit("1970-01-01").cast("date")))
        .withColumn("_advanced", F.col("feature_b_events") + F.col("feature_c_events"))
        .withColumn("_all_features", F.col("feature_a_events") + F.col("_advanced"))
    )

    # Calendar-day windows that only look backwards.
    account_days = Window.partitionBy("tenant_id", "account_id").orderBy("_day")
    last_7 = account_days.rangeBetween(-6, 0)
    last_30 = account_days.rangeBetween(-29, 0)
    prior_30 = account_days.rangeBetween(-59, -30)
    history = account_days.rangeBetween(Window.unboundedPreceding, 0)

    def ratio(numerator, denominator):
        return F.when(denominator > 0, numerator / denominator)

    valid_dates = (
        (F.col("created_date") <= F.col("subscription_start_date"))
        & (F.col("subscription_start_date") <= F.col("snapshot_date"))
        & (F.col("renewal_date") > F.col("snapshot_date"))
    )

    return (
        base
        .withColumn("active_users_avg_7d", F.avg("active_users").over(last_7))
        .withColumn("active_users_avg_30d", F.avg("active_users").over(last_30))
        .withColumn("_users_prior_30d", F.avg("active_users").over(prior_30))
        .withColumn("sessions_avg_30d", F.avg("sessions").over(last_30))
        .withColumn("_api_30d", F.avg("api_calls").over(last_30))
        .withColumn("_api_prior_30d", F.avg("api_calls").over(prior_30))
        .withColumn("_advanced_30d", F.sum("_advanced").over(last_30))
        .withColumn("_all_features_30d", F.sum("_all_features").over(last_30))
        .withColumn("critical_tickets_avg_7d", F.avg("critical_open_tickets").over(last_7))
        .withColumn("history_days_available", F.count("*").over(history))
        .withColumn("seat_utilisation", ratio(F.col("active_users"), F.col("licensed_seats")))
        .withColumn("seat_utilisation_30d", ratio(F.col("active_users_avg_30d"), F.col("licensed_seats")))
        .withColumn("usage_change_30d", ratio(F.col("active_users_avg_30d"), F.col("_users_prior_30d")) - 1)
        .withColumn("api_change_30d", ratio(F.col("_api_30d"), F.col("_api_prior_30d")) - 1)
        .withColumn("advanced_feature_share_30d", ratio(F.col("_advanced_30d"), F.col("_all_features_30d")))
        .withColumn("feature_ready", F.col("history_days_available") >= 60)
        .withColumn("subscription_dates_valid", valid_dates)
        .withColumn(
            "days_to_renewal",
            F.when(valid_dates, F.datediff("renewal_date", "snapshot_date")),
        )
        .drop(
            "_day", "_advanced", "_all_features", "_users_prior_30d",
            "_api_30d", "_api_prior_30d", "_advanced_30d", "_all_features_30d",
        )
    )
```

**What the features mean:**

| Feature | Meaning |
|---|---|
| `seat_utilisation`, `seat_utilisation_30d` | Share of paid seats actually used |
| `usage_change_30d` | Last 30 days' average users vs. the previous 30 days |
| `api_change_30d` | Same comparison for API calls |
| `advanced_feature_share_30d` | Depth of product adoption |
| `critical_tickets_avg_7d` | Recent support pressure |
| `feature_ready` | At least 60 days of history, so the trend features are meaningful |
| `days_to_renewal` | Days until renewal; null when the synthetic subscription dates are inconsistent |

### Cell 2: build and save the Gold tables

```python
tables = {
    "usage": spark.table("silver_usage_daily"),
    "support": spark.table("silver_support_daily"),
    "interaction": spark.table("silver_interaction_daily"),
    "subscription": spark.table("silver_subscription_daily"),
    "account": spark.table("silver_account"),
}

gold = build_customer360(**tables)

FORBIDDEN = {
    "will_churn", "churn_date", "cancel_date", "days_to_churn",
    "label_churn_next_90d", "subscription_status",
}
assert not FORBIDDEN & set(gold.columns), "Future-outcome column in Gold features"

(
    gold.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("gold_customer360_daily")
)

outcomes = (
    spark.table("silver_churn_outcomes")
    .withColumn(
        "at_risk_population",
        F.col("churn_date").isNull() | (F.col("snapshot_date") < F.col("churn_date")),
    )
)
(
    outcomes.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("gold_training_outcomes")
)
print("Gold tables written")
```

This is the slowest step: expect several minutes on a small capacity.

**Two Gold tables are created:**

- `gold_customer360_daily`: features only — used by the model, reports, and replay.
- `gold_training_outcomes`: labels only — used for training and evaluation, never in operational reports.

`at_risk_population = false` marks the cancellation-day row, which must be excluded from training.

### Cell 3: validate the Gold dataset

```python
gold = spark.table("gold_customer360_daily")
outcomes = spark.table("gold_training_outcomes")

gold_rows = gold.count()
duplicates = gold.groupBy(*KEYS).count().filter("count > 1").count()
unmatched = gold.join(outcomes, KEYS, "left_anti").count()

print(f"Gold rows: {gold_rows:,} | duplicate keys: {duplicates} | rows without outcome: {unmatched}")
assert gold_rows == 6_669_117
assert duplicates == 0 and unmatched == 0

gold.groupBy("feature_ready").count().show()
gold.groupBy("subscription_dates_valid").count().show()

(
    gold.join(outcomes, KEYS)
    .filter("feature_ready AND at_risk_population")
    .groupBy("label_churn_next_90d")
    .agg(
        F.count("*").alias("rows"),
        F.round(F.avg("seat_utilisation_30d"), 3).alias("seat_util_30d"),
        F.round(F.avg("usage_change_30d"), 3).alias("usage_change_30d"),
        F.round(F.avg("critical_tickets_avg_7d"), 2).alias("critical_7d"),
        F.round(F.avg("days_since_last_csm_touch"), 1).alias("days_since_touch"),
    )
    .orderBy("label_churn_next_90d")
    .show()
)
```

**Expected:**

- 6,669,117 rows with no duplicates.
- Every Gold row has an outcome row.
- Label `1` rows show lower seat utilisation, more negative usage change, more critical tickets, and longer gaps since CSM contact than label `0` rows.

### Cell 4: leakage test (features must not use future data)

```python
import math

churner = (
    outcomes.filter("will_churn = 1")
    .orderBy("account_id")
    .select("tenant_id", "account_id", "churn_date")
    .first()
)
cutoff = (
    spark.range(1)
    .select(F.date_sub(F.lit(churner["churn_date"]), 45).alias("d"))
    .first()["d"]
)
print("Testing", churner["account_id"], "at", cutoff)

def only_account(df, up_to=None):
    df = df.filter(
        (F.col("tenant_id") == churner["tenant_id"])
        & (F.col("account_id") == churner["account_id"])
    )
    if up_to is not None and "snapshot_date" in df.columns:
        df = df.filter(F.col("snapshot_date") <= F.lit(up_to))
    return df

full_row = only_account(gold).filter(F.col("snapshot_date") == F.lit(cutoff)).first().asDict()
truncated = {name: only_account(df, cutoff) for name, df in tables.items()}
recomputed_row = (
    build_customer360(**truncated)
    .filter(F.col("snapshot_date") == F.lit(cutoff))
    .first().asDict()
)

differences = []
for column, value in full_row.items():
    other = recomputed_row[column]
    if isinstance(value, float) and isinstance(other, float):
        same = math.isclose(value, other, rel_tol=1e-9, abs_tol=1e-9)
    else:
        same = value == other
    if not same:
        differences.append((column, value, other))

print("Differences:", differences or "none")
assert not differences, "A feature changed when future rows were removed"
```

**Expected:** `Differences: none`. This shows that removing everything after the cutoff date doesn't change the features at that date.

**Stop session** when done.

---

## Part 9: confirm in the SQL analytics endpoint

1. Open the Lakehouse → top-right switcher → **SQL analytics endpoint**.
2. Select **New SQL query**.
3. Run:

```sql
SELECT COUNT(*) AS rows, COUNT(DISTINCT account_id) AS accounts,
       MIN(snapshot_date) AS first_date, MAX(snapshot_date) AS last_date
FROM gold_customer360_daily;

SELECT TOP 10 account_id, snapshot_date, seat_utilisation_30d,
       usage_change_30d, critical_tickets_avg_7d, days_since_last_csm_touch
FROM gold_customer360_daily
WHERE feature_ready = 1
ORDER BY usage_change_30d ASC;
```

If a table is missing, wait a minute and refresh; the endpoint syncs metadata with a short delay. If schemas are enabled, use `dbo.gold_customer360_daily`.

---

## Part 10: finish and hand off

**Final table list:**

| Layer | Table | Rows |
|---|---|---|
| Bronze | `bronze_master_daily` | 6,669,117 |
| Silver | `silver_account`, `silver_contact` | 10,000 each |
| Silver | `silver_subscription_daily`, `silver_usage_daily`, `silver_support_daily`, `silver_interaction_daily`, `silver_churn_outcomes` | 6,669,117 each |
| Gold | `gold_customer360_daily` | 6,669,117 |
| Gold | `gold_training_outcomes` | 6,669,117 |

**Handoffs:**

- **Irfan:** Train from `gold_customer360_daily` joined to `gold_training_outcomes`, filtered to `feature_ready AND at_risk_population`.
- **Lokesh:** Use `gold_customer360_daily` for account history. Never put `gold_training_outcomes` in operational report pages.
- **Sujith:** Wait for Irfan's scored output; don't replay raw Gold rows as risk events.
- **Archi:** Record the Gold validation output and the subscription-date warning counts as known data limitations.

**Cost hygiene:**

- **Stop session** in each notebook when finished.
- Check **Cost analysis** in the Azure resource group daily.
- Pause `capacity2447013` only after confirming nobody else is using it, and only if the sandbox allows it.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Path does not exist` | Check the Lakehouse is attached to the notebook and the folder and file name match exactly |
| `Table or view not found` | Run the previous notebook first; check the attached Lakehouse is `lh_customer_intelligence` |
| Spark session won't start or is very slow | Another notebook is probably running; stop other sessions and retry |
| Out-of-memory error | Never call `toPandas()` on full tables; rerun the cell |
| `Column … cannot be resolved` | A table was saved with a different schema; rerun the earlier notebook |
| Assertion failed | Copy the printed values and stop; don't change expected numbers |
| `try_cast` not recognised | Check the workspace Spark runtime version (Workspace settings → Data Engineering/Science → Spark settings) and report it to Somnath |
