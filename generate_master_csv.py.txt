#!/usr/bin/env python3
"""Generate a synthetic SaaS B2B daily-snapshot dataset for 90-day churn early warning.

Output: one denormalized master CSV, one row per (account_id, snapshot_date).
Rows are written in account batches so peak memory stays small.
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- parameters
SEED = 42
N_ACCOUNTS = 10_000
START_DATE = date(2024, 1, 1)
N_DAYS = 730                      # 2 years of daily snapshots
CHURN_RATE = 0.25                 # share of accounts that churn within the 2 years
PRE_CHURN_MIN_DAYS = 60           # degradation window lower bound
PRE_CHURN_MAX_DAYS = 120          # degradation window upper bound
HORIZON_DAYS = 90                 # labeling horizon
BATCH_ACCOUNTS = 250              # accounts per CSV flush (~182k rows)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUT_FILE = os.path.join(OUT_DIR, "master_saas_b2b_daily_10k_2y_2024.csv")

COLUMNS = [
    # identifiers & dates
    "snapshot_date", "account_id", "tenant_id",
    # account
    "account_name", "domain", "industry", "region", "employee_count",
    "created_date", "arr_usd", "csm_owner",
    # contact
    "primary_contact_id", "primary_contact_role", "primary_contact_created_date",
    # subscription
    "subscription_id", "plan_tier", "seats_purchased", "mrr_usd",
    "subscription_start_date", "renewal_date", "subscription_status", "cancel_date",
    # daily usage
    "active_users", "sessions", "feature_a_events", "feature_b_events",
    "feature_c_events", "api_calls", "licensed_seats",
    # support
    "tickets_created_today", "tickets_closed_today", "critical_open_tickets",
    "tickets_created_30d", "avg_ttr_days_60d",
    # interactions
    "interactions_30d", "days_since_last_csm_touch", "no_show_rate_90d",
    # labels
    "will_churn", "churn_date", "label_churn_next_90d", "days_to_churn",
]

INDUSTRIES = ["Software", "Financial Services", "Healthcare", "Retail",
              "Manufacturing", "Logistics", "Education", "Media",
              "Energy", "Professional Services"]
REGIONS = ["NA-East", "NA-West", "EMEA-UK", "EMEA-DACH", "EMEA-Nordics",
           "APAC-ANZ", "APAC-India", "LATAM"]
PLAN_TIERS = ["Starter", "Growth", "Business", "Enterprise"]
PLAN_WEIGHTS = [0.30, 0.34, 0.24, 0.12]
PLAN_PRICE_PER_SEAT = {"Starter": 18.0, "Growth": 35.0, "Business": 62.0, "Enterprise": 110.0}
CONTACT_ROLES = ["Admin", "Champion", "Economic Buyer", "End User", "IT Owner"]
CSM_OWNERS = [f"csm_{i:03d}" for i in range(1, 61)]

DATE_STRINGS = np.array(
    [(START_DATE + timedelta(days=i)).isoformat() for i in range(N_DAYS)]
)
DAY_OF_WEEK = np.array([(START_DATE + timedelta(days=i)).weekday() for i in range(N_DAYS)])
WEEKEND_FACTOR = np.where(DAY_OF_WEEK >= 5, 0.32, 1.0)


def build_static_attributes(rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Per-account attributes that do not vary by snapshot_date."""
    account_ids = np.array([f"ACC{i:06d}" for i in range(1, N_ACCOUNTS + 1)])
    plan_tier = rng.choice(PLAN_TIERS, size=N_ACCOUNTS, p=PLAN_WEIGHTS)
    seat_base = {"Starter": 12, "Growth": 45, "Business": 140, "Enterprise": 600}
    seats = np.array([
        max(3, int(rng.lognormal(mean=np.log(seat_base[t]), sigma=0.55)))
        for t in plan_tier
    ])
    mrr = np.round(seats * np.array([PLAN_PRICE_PER_SEAT[t] for t in plan_tier])
                   * rng.uniform(0.85, 1.15, N_ACCOUNTS), 2)

    # account creation 0-5 years before the snapshot window starts
    created_offsets = rng.integers(30, 1825, N_ACCOUNTS)
    created_dates = np.array([
        (START_DATE - timedelta(days=int(o))).isoformat() for o in created_offsets
    ])
    # subscription starts on/after account creation, before the window ends
    sub_start_offsets = rng.integers(-1800, 600, N_ACCOUNTS)
    sub_start_dates = np.array([
        (START_DATE + timedelta(days=int(o))).isoformat() for o in sub_start_offsets
    ])

    churn_flag = rng.random(N_ACCOUNTS) < CHURN_RATE
    # churn can only happen after enough history exists to label a 90d horizon
    churn_offset = np.where(
        churn_flag,
        rng.integers(PRE_CHURN_MAX_DAYS + HORIZON_DAYS, N_DAYS, N_ACCOUNTS),
        -1,
    )

    industry = rng.choice(INDUSTRIES, N_ACCOUNTS)

    return {
        "account_id": account_ids,
        "tenant_id": np.array([f"TEN{i:06d}" for i in range(1, N_ACCOUNTS + 1)]),
        "account_name": np.array([f"Account {i:05d} {ind}" for i, ind in
                                  enumerate(industry, start=1)]),
        "industry": industry,
        "region": rng.choice(REGIONS, N_ACCOUNTS),
        "employee_count": (seats * rng.uniform(3, 14, N_ACCOUNTS)).astype(int),
        "created_date": created_dates,
        "csm_owner": rng.choice(CSM_OWNERS, N_ACCOUNTS),
        "contact_role": rng.choice(CONTACT_ROLES, N_ACCOUNTS),
        "plan_tier": plan_tier,
        "seats": seats,
        "mrr": mrr,
        "sub_start_date": sub_start_dates,
        "engagement": rng.uniform(0.22, 0.88, N_ACCOUNTS),
        "sessions_per_user": rng.uniform(1.2, 4.5, N_ACCOUNTS),
        "api_per_session": rng.uniform(6, 60, N_ACCOUNTS),
        "pre_churn_window": rng.integers(PRE_CHURN_MIN_DAYS, PRE_CHURN_MAX_DAYS + 1, N_ACCOUNTS),
        "churn_offset": churn_offset,
    }


def days_since_last_touch(touched: np.ndarray) -> np.ndarray:
    """Vectorized 'days since the most recent CSM touch' from a boolean touch series."""
    n = touched.shape[0]
    idx = np.arange(n)
    last = np.where(touched, idx, -1)
    last = np.maximum.accumulate(last)
    return np.where(last < 0, idx + 1, idx - last)


def build_account_frame(i: int, s: dict[str, np.ndarray], rng: np.random.Generator) -> pd.DataFrame:
    churn_offset = int(s["churn_offset"][i])
    will_churn = churn_offset >= 0
    # churned accounts stop emitting snapshots on their cancel date
    n = N_DAYS if not will_churn else churn_offset + 1
    day = np.arange(n)

    if will_churn:
        days_to_churn = churn_offset - day
        window = int(s["pre_churn_window"][i])
        distress = np.clip((window - days_to_churn) / window, 0.0, 1.0)
        churn_date = DATE_STRINGS[churn_offset]
        label = ((days_to_churn > 0) & (days_to_churn <= HORIZON_DAYS)).astype(np.int8)
    else:
        days_to_churn = np.full(n, -1, dtype=np.int32)
        distress = np.zeros(n, dtype=np.float64)
        churn_date = ""
        label = np.zeros(n, dtype=np.int8)

    seats = int(s["seats"][i])
    health = 1.0 - 0.88 * distress              # usage multiplier, degrades pre-churn
    growth = 1.0 + 0.00025 * day                # mild organic growth
    noise = rng.normal(1.0, 0.11, n)

    base_users = seats * float(s["engagement"][i]) * health * growth * WEEKEND_FACTOR[:n] * noise
    active_users = np.clip(np.rint(base_users), 0, seats).astype(np.int32)

    sessions = np.rint(active_users * float(s["sessions_per_user"][i])
                       * rng.normal(1.0, 0.13, n)).clip(0).astype(np.int32)
    feature_a = np.rint(sessions * rng.uniform(1.5, 4.0) * rng.normal(1.0, 0.15, n)).clip(0).astype(np.int32)
    feature_b = np.rint(sessions * rng.uniform(0.4, 1.6) * health * rng.normal(1.0, 0.18, n)).clip(0).astype(np.int32)
    feature_c = np.rint(sessions * rng.uniform(0.1, 0.8) * health * rng.normal(1.0, 0.25, n)).clip(0).astype(np.int32)
    api_calls = np.rint(sessions * float(s["api_per_session"][i])
                        * rng.normal(1.0, 0.2, n)).clip(0).astype(np.int64)

    # --- support signals: volume and severity rise as distress rises
    tickets_created = rng.poisson(0.04 * np.sqrt(seats) * (1.0 + 2.5 * distress)).astype(np.int32)
    tickets_closed = rng.poisson(0.04 * np.sqrt(seats) * (1.0 + 1.2 * distress)).astype(np.int32)
    critical_open = rng.poisson(0.08 + 1.6 * distress).astype(np.int32)
    kernel30 = np.ones(30)
    tickets_30d = np.rint(
        np.convolve(tickets_created, kernel30)[:n]
    ).astype(np.int32)
    avg_ttr_60d = np.round(1.8 + 7.5 * distress + rng.normal(0, 0.4, n), 2).clip(0.2)

    # --- interaction signals
    interactions_30d = rng.poisson(np.clip(6.0 * (1.0 - 0.75 * distress), 0.2, None)).astype(np.int32)
    touch_prob = np.clip(0.07 * (1.0 - 0.8 * distress), 0.002, 1.0)
    touched = rng.random(n) < touch_prob
    since_touch = days_since_last_touch(touched).astype(np.int32)
    no_show_rate = np.round(np.clip(0.04 + 0.4 * distress + rng.normal(0, 0.03, n), 0, 1), 3)

    sub_start = date.fromisoformat(str(s["sub_start_date"][i]))
    renewal_dates = []
    for d in day:
        snap = START_DATE + timedelta(days=int(d))
        years = max(0, (snap - sub_start).days // 365 + 1)
        renewal_dates.append((sub_start + timedelta(days=365 * years)).isoformat())

    status = np.full(n, "Active", dtype=object)
    cancel_col = np.full(n, "", dtype=object)
    if will_churn:
        pending = days_to_churn <= 30
        status[pending] = "Pending Cancellation"
        status[-1] = "Churned"
        cancel_col[:] = churn_date

    mrr = float(s["mrr"][i])
    return pd.DataFrame({
        "snapshot_date": DATE_STRINGS[:n],
        "account_id": s["account_id"][i],
        "tenant_id": s["tenant_id"][i],
        "account_name": s["account_name"][i],
        "domain": f"{str(s['account_id'][i]).lower()}.example.com",
        "industry": s["industry"][i],
        "region": s["region"][i],
        "employee_count": int(s["employee_count"][i]),
        "created_date": s["created_date"][i],
        "arr_usd": round(mrr * 12, 2),
        "csm_owner": s["csm_owner"][i],
        "primary_contact_id": f"CON{i + 1:06d}",
        "primary_contact_role": s["contact_role"][i],
        "primary_contact_created_date": s["created_date"][i],
        "subscription_id": f"SUB{i + 1:06d}",
        "plan_tier": s["plan_tier"][i],
        "seats_purchased": seats,
        "mrr_usd": mrr,
        "subscription_start_date": s["sub_start_date"][i],
        "renewal_date": renewal_dates,
        "subscription_status": status,
        "cancel_date": cancel_col,
        "active_users": active_users,
        "sessions": sessions,
        "feature_a_events": feature_a,
        "feature_b_events": feature_b,
        "feature_c_events": feature_c,
        "api_calls": api_calls,
        "licensed_seats": seats,
        "tickets_created_today": tickets_created,
        "tickets_closed_today": tickets_closed,
        "critical_open_tickets": critical_open,
        "tickets_created_30d": tickets_30d,
        "avg_ttr_days_60d": avg_ttr_60d,
        "interactions_30d": interactions_30d,
        "days_since_last_csm_touch": since_touch,
        "no_show_rate_90d": no_show_rate,
        "will_churn": np.int8(1 if will_churn else 0),
        "churn_date": churn_date,
        "label_churn_next_90d": label,
        "days_to_churn": days_to_churn,
    }, columns=COLUMNS)


def main() -> None:
    rng = np.random.default_rng(SEED)
    static = build_static_attributes(rng)

    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(OUT_FILE):
        os.remove(OUT_FILE)

    total_rows = 0
    header_written = False

    for start in range(0, N_ACCOUNTS, BATCH_ACCOUNTS):
        end = min(start + BATCH_ACCOUNTS, N_ACCOUNTS)
        frames = [build_account_frame(i, static, rng) for i in range(start, end)]
        batch = pd.concat(frames, ignore_index=True)
        batch.to_csv(
            OUT_FILE,
            mode="a",
            index=False,
            header=not header_written,
            columns=COLUMNS,
        )
        header_written = True
        total_rows += len(batch)
        print(f"Wrote accounts {start + 1}..{end} (rows so far: {total_rows:,})", flush=True)

    print(f"Total rows: {total_rows:,}")
    print(f"Done: {OUT_FILE}")


if __name__ == "__main__":
    main()
