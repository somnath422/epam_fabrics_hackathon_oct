# Lokesh: beginner Power BI runbook

[Handbook](./README.md) | [Daily board](./01_Day_by_Day_Plan.md) | [Table contracts](./02_Shared_Contracts_and_Acceptance.md)

You are Developer 3. No prior Power BI experience is required. Own the semantic model and three-page report, not ML training or source cleanup.

## 1. Understand five terms first

| Term | Plain-language meaning |
|---|---|
| Lakehouse table | Data prepared by Ashish/Irfan/Somnath |
| Semantic model | Tables, types, calculations, and security used by reports |
| Report | Interactive pages with charts, cards, and filters |
| Measure | A DAX calculation evaluated in the current filters |
| Slicer | A visible control letting users choose a date/account/region |

Direct Lake reads Delta-backed data through Fabric. It does not mean report visuals instantly redraw every time an Eventstream event arrives. Model refresh/framing and browser visual refresh are separate operations.

## 2. Tools and prerequisites

- Use `https://app.fabric.microsoft.com` in a browser with your named sandbox identity.
- Ask Somnath for workspace access and permission to create/edit the semantic model and report.
- Power BI Desktop is Windows-only; the recommended browser path works on Mac.
- Do not install Power BI Desktop on the Mac or start a VM.
- On capacities below F64, sharing/viewing Power BI content generally requires the appropriate per-user Power BI license. Verify the sandbox assignment rather than promising free viewers.
- Do not use Publish to web; it can expose the report publicly.

## October 29: make a tiny first report

### B01: get fixture data without blocking on the model

Ask Somnath to have the producer create a separate fixture table matching `gold_report_portfolio` with:

- Two or three accounts.
- At least three dates per account.
- At least two tenant IDs.
- Numeric score/ARR/trend fields, date-typed snapshots.
- `is_fixture=true`.
- All required metadata and driver strings.

Fixture values are design data, not predictive evidence. Use a fixture item name and put "DEVELOPMENT FIXTURE" on the report.

### B02: create a semantic model in the browser

Menu labels vary slightly:

1. Open workspace -> Lakehouse.
2. Locate **New semantic model**. It may also be available from the SQL analytics endpoint or OneLake catalog.
3. If tables are not visible through the endpoint yet, wait for metadata synchronization and refresh.
4. Choose the fixture table only.
5. Name the development model `sm_customer_intelligence_dev`.
6. Create/open it.
7. Check:
   - `snapshot_date`: Date.
   - `risk_score` and trends: decimal number.
   - `arr_usd`: decimal/currency.
   - IDs: text.
8. Select **Create report** from the model, or select the model in the workspace -> New report.
9. Save as `rpt_customer_intelligence_dev`.

Do not assume the Lakehouse automatically creates an editable default semantic model. Create an explicit model.

If report creation is available but model editing/New measure is absent, ask Somnath to check edit/Build permissions and tenant restrictions. Do not lose hours looking for a hidden button.

### First three visuals

1. Add a **Table** visual; drag account name, date, risk score, and ARR into it.
2. Add a **Slicer**; drag `snapshot_date` into it, choose the actual date field rather than an automatic hierarchy.
3. Format slicer as list/dropdown; turn **Single select** on.
4. Select one date.
5. Add a **Card**, initially showing a simple count for learning.
6. Save and reopen.

**Exit:** you can explain how a date slicer changes a visual.

## October 30: build the real semantic model and measures

### B03: use a deliberately simple model

The beginner production model starts with `gold_report_portfolio`, one approved model version per account/date. It already contains metadata and history features.

Do not join risk history directly to actions as many-to-many. Do not build relationships on account ID alone where multiple tenant/date rows exist.

Keep `gold_retention_actions` disconnected for the initial action panel. It has its own filters. Label this; a portfolio slicer will not automatically filter a disconnected action table.

The team can later add tested dimensions/relationships, but that is not required for the first correct report.

### B04: add measures

In the semantic model editor, select the reporting table -> **New measure**. Paste one measure at a time, name it, save it, and verify it appears in the report's Data pane.

These DAX expressions assume the exact table name `gold_report_portfolio`.

```dax
Date Selection Message =
IF(
    HASONEVALUE('gold_report_portfolio'[snapshot_date]),
    "Historical as-of: "
        & FORMAT(SELECTEDVALUE('gold_report_portfolio'[snapshot_date]), "yyyy-MM-dd"),
    "Select exactly one historical date"
)
```

```dax
Scored Accounts =
IF(
    HASONEVALUE('gold_report_portfolio'[snapshot_date]),
    DISTINCTCOUNT('gold_report_portfolio'[account_id]),
    BLANK()
)
```

```dax
Portfolio ARR =
IF(
    HASONEVALUE('gold_report_portfolio'[snapshot_date]),
    SUM('gold_report_portfolio'[arr_usd]),
    BLANK()
)
```

```dax
High Risk Accounts =
IF(
    HASONEVALUE('gold_report_portfolio'[snapshot_date]),
    CALCULATE(
        DISTINCTCOUNT('gold_report_portfolio'[account_id]),
        'gold_report_portfolio'[risk_band] = "High"
    ),
    BLANK()
)
```

```dax
Risk Weighted ARR =
IF(
    HASONEVALUE('gold_report_portfolio'[snapshot_date]),
    SUM('gold_report_portfolio'[estimated_arr_exposure]),
    BLANK()
)
```

```dax
Last Scored UTC =
IF(
    HASONEVALUE('gold_report_portfolio'[snapshot_date]),
    MAX('gold_report_portfolio'[scored_at]),
    BLANK()
)
```

IDs in this source are globally unique. If that changes, use a producer-created tenant/account key for distinct counts.

Check `High Risk Accounts` interaction with risk-band slicers: this card intentionally calculates High under the other filters. Label it clearly, or use `KEEPFILTERS` if the intended UX is intersection with a selected band.

Format ARR measures as USD and risk score as percentage. Do not summarize account IDs numerically.

**Important:** these portfolio measures return blank for multiple dates because summing account-day ARR across dates is wrong. The message explains the required selection.

## October 31: replace fixtures and reconcile

### B05

1. Ask Somnath for the accepted reporting table and release ID.
2. Create `sm_customer_intelligence` using the real table.
3. Recreate measures in this production model.
4. Create `rpt_customer_intelligence` and transfer/rebuild the simple visuals.
5. Apply report filter `is_fixture=false`.
6. Check one model version per account/date.
7. Set one historical default date within the actual scored range; do not use today's date.
8. Compare account count, ARR, and exposure to Somnath's notebook totals on the same date/cohort.
9. Remove or clearly separate development reports from the accepted presentation.

Keep the old fixture report only as development reference, not as the fallback "working solution."

## November 1: build the three pages

### Page 1: Portfolio overview

1. Add a page; rename it **Portfolio**.
2. Add a text box: "Synthetic B2B SaaS | Historical scoring | Reporting cohort: [actual scope]".
3. Add a single-select snapshot-date slicer.
4. Add optional region, industry, and plan slicers.
5. Add cards using the measures above:
   - Scored Accounts.
   - High Risk Accounts.
   - Portfolio ARR.
   - Risk Weighted ARR.
6. Add the date-selection message.
7. Add bar chart: industry on axis, risk-weighted ARR as value.
8. Add bar chart: risk band on axis, account count as value for selected date.
9. Show model version, Last Scored UTC, and cohort coverage.
10. Add tooltip/text: "Risk-weighted ARR is a prioritization proxy unless calibration is established."

Do not call scored-account count "all active customers" if the model/report uses a bounded cohort.

### Page 2: Retention workbench

1. Add page **Retention Workbench**.
2. Add the same single-select date slicer.
3. Add owner, segment, plan, and risk-band slicers.
4. Add table:

```text
account_id, account_name, risk_score, arr_usd,
estimated_arr_exposure, primary_segment, top_driver_1,
recommended_play, csm_owner
```

5. Sort descending by estimated exposure; optionally show High-risk accounts.
6. Use conditional formatting for risk score. Keep text labels so color is not the only signal.
7. Add a separate action table from `gold_retention_actions` with account, owner, status, trigger date, notification status.
8. Give that disconnected table its own account/status filters and label it "Action register - separate filters."
9. Explain that editing a Power BI table cell does not write back to Delta.

For the first version, Somnath may update approved action statuses through a controlled notebook and refresh the report. That is a demonstration of action tracking, not a production operational UI.

### Page 3: Account 360

Use the **same portfolio table**, which includes historical metrics:

1. Add page **Account 360**.
2. Add single-select `account_id` slicer; show tenant/account context.
3. Do not copy the single-date page filter from Portfolio to this page.
4. Add line chart:
   - X: `snapshot_date` actual Date, not hierarchy.
   - Y: `risk_score` with MAX aggregation.
5. Add separate usage chart with `active_users_avg_7d` and `active_users_avg_30d`.
6. Add separate support chart with `critical_open_tickets`.
7. Avoid putting usage counts and a probability on the same scale.
8. Add a date-range slicer limited to the approved history.
9. Add a table of date, top driver, and recommended play to show how the explanation changes.
10. Add optional buttons for page navigation. The simple version requires selecting the account on this page.

Do not claim automatic drill-through unless you have configured and tested its filter transfer. Manual account selection is reliable and acceptable.

If using Sync slicers, sync the date slicer only between Portfolio and Workbench; syncing a single date to Account 360 collapses the timeline.

## November 2: integrate actions and replay

### B08

1. Verify the action register includes the replay account.
2. After publication, refresh the semantic model/framing through the supported menu.
3. Refresh report visuals separately.
4. Confirm new data appears; capture the time.
5. Use Eventhouse/Activator views for the live replay portion if Power BI refresh is not fast enough.
6. Do not promise per-event animation in Power BI without measuring it.

The account risk timeline may already be prepared historical data. Label it as such.

## November 3: security and failure testing

### B09: simple RLS demonstration

Use synthetic tenants only for an initial static-role test:

1. Model editor -> Manage roles/Security, if enabled.
2. Create role `DemoTenant000001`.
3. Add table filter:

```dax
[tenant_id] = "TEN000001"
```

4. Apply an equivalent tenant filter to **every exposed tenant-bearing table**, including disconnected actions/history if included.
5. Save.
6. Use Test as role to inspect.
7. Assign the test identity to the role in semantic-model security where available.
8. Open as a workspace **Viewer** and prove another tenant is not visible.
9. Confirm the Viewer has no independent broad Lakehouse access.

Workspace Admin/Member/Contributor roles are not valid end-user RLS tests. A visual filter is not security. Do not add a user to multiple roles casually; role permissions can combine.

If browser role editing is unavailable, check permissions and supported tooling with Somnath. Mark RLS planned until actually tested. A dynamic Entra user-to-tenant mapping is a production extension, not required for this static demo.

### Other tests

- Two dates selected -> portfolio measures blank and guidance visible.
- No matching account -> empty state clearly understandable.
- Model version shown matches release.
- No future outcomes exposed.
- Refresh does not duplicate rows or ARR.
- Page 3 retains a timeline, not a single date.
- Actions do not misleadingly respond to disconnected slicers.

## November 4: final polish

### B10

- Consistent colors, readable fonts, minimal scrolling.
- No default "Sum of account_id" fields.
- Percentage and USD units clear.
- Historical and operational timestamps distinguished.
- Synthetic data label present.
- No misleading guarantee or "ARR saved" headline.
- Reconcile the final selected date again after cosmetic changes.

## November 5-6: sharing and exports

### B11

1. Verify intended judges/team can open through the permitted sharing route.
2. Check license and permissions using an intended viewer identity.
3. Export screenshots/PDF where allowed.
4. Download report/model artifacts if supported. Do not assume every Direct Lake artifact downloads to PBIX.
5. Save measure definitions, model table list, RLS rules, and recreation steps even if download is unavailable.
6. Give Archi a clean browser view and fixed navigation order.

## Browser blocked: fallback

1. Have Somnath check workspace role, Build/edit permissions, tenant restrictions, and capacity.
2. If a Windows machine is already available, use Power BI Desktop with the approved connection to the Fabric semantic model/SQL endpoint.
3. For an Import fallback, use only a bounded approved reporting extract; label it Import, not Direct Lake.
4. If neither route is available, escalate and document the limitation. Screenshots of fixtures are not a completed Power BI implementation.

Official reference: [Direct Lake model creation](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-develop).
