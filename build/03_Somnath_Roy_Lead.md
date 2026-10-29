# Somnath Roy: lead, platform, integration, and release

[Handbook](./README.md) | [Daily board](./01_Day_by_Day_Plan.md) | [Contracts](./02_Shared_Contracts_and_Acceptance.md)

## Your responsibility

Make six parallel workstreams produce one demonstrable system. You own platform access, compute coordination, integration, release decisions, and truthful architecture claims. You do not need to write all four developers' code.

| Member | Workstream |
|---|---|
| Ashish | Source, Silver, Gold features, data quality |
| Irfan | Model, experiments, scoring, explanations |
| Lokesh | Semantic model, Power BI, report RLS |
| Sujith | Replay, Eventstream, Eventhouse, Activator |
| Archi S | Business rules, acceptance, value model, presentation |

## October 29: establish the environment

### S01: confirm constraints before provisioning

1. Sign in to `https://portal.azure.com` with the sandbox identity.
2. Record subscription/resource group, sandbox expiry, current spend, and permitted region in an approved team location. Do not copy tokens or passwords.
3. Search for Microsoft Fabric capacities. Reuse an existing assigned capacity.
4. Open `https://app.fabric.microsoft.com` with the same tenant identity.
5. Check whether a capacity is already available for workspace assignment.
6. Only if none exists, follow [Microsoft capacity setup](https://learn.microsoft.com/en-us/fabric/enterprise/buy-capacity), select F2, inspect price, and use the provided resource group.
7. If quota/tenant access blocks provisioning, escalate to sandbox support. Azure Owner does not imply Fabric tenant admin.
8. Confirm November 6 submission target, permitted video length, required artifacts, and whether showcase access survives sandbox deletion.

### S02: named identities and permissions

1. Request organizer-approved named access for all six people.
2. Do not distribute the one provided account's password.
3. If only one identity is permitted, ask support for the collaboration method. In parallel, team members can author local notebooks and fixture reports without accessing that account.
4. Give builders only the roles needed to build; use Viewer access for business acceptance where supported.
5. Keep an access matrix: person, workspace role, item permissions, purpose.
6. Assign a separate Viewer/test identity for RLS testing if available.

### S03: create workspace and Lakehouse

1. Fabric -> Workspaces -> New workspace -> `ws_customer_intelligence`.
2. Assign the provided F2 in workspace license/capacity settings.
3. New item -> Lakehouse -> `lh_customer_intelligence`.
4. Leave schema configuration at the supported default; tell all developers whether `dbo` appears.
5. Verify creation of a notebook attached to this Lakehouse.
6. Let Ashish own ingestion from this point.

### S04: agree contracts and working method

- Read [contracts](./02_Shared_Contracts_and_Acceptance.md) together for 30 minutes.
- Confirm each role owns its listed items.
- Book shared Spark windows; do not have everyone start a session as a test.
- Create an approved shared repository if permitted. Commit notebooks/scripts/docs, not the giant CSV or secrets.
- Confirm fixture tables/items are separate from accepted outputs.

**Exit:** each member has a productive task; no one waits for the full dataset just to start.

## October 30: define orchestration and release state

### S05: create the run order

For the first run, manual notebook execution is acceptable:

```text
01_ingest_validate  (one-time source ingestion)
02_silver_gold
03_train_evaluate  (model release only, not every scoring run)
04_score_explain
05_publish_actions_reports
06_replay_scored_events  (bounded, manually started)
```

In Fabric, optionally create a Data pipeline:

1. Workspace -> New item -> Data pipeline -> `pl_customer_intelligence`.
2. Add Notebook activities for feature preparation, scoring, and publication.
3. Select each owner's existing notebook; verify the attached Lakehouse.
4. Connect activities using **success** dependencies.
5. Pass an agreed as-of date/run ID through notebook parameter cells if supported. Otherwise use a single release config table read consistently by every stage.
6. Do not attach training to every scheduled inference run.
7. Disable schedule until manual integration passes.
8. Let failures stop downstream publication. Do not connect failed activities to a success-shaped publishing path.

Create `gold_run_log` and agree which stage writes each row. Log starting, succeeded, failed, and row counts. Error handling may log and re-raise; it must not suppress a failure.

## October 31: first integration

### S06: assemble the first real vertical slice

1. Ask Ashish for actual feature schema and passed quality checks.
2. Ask Irfan for an approved model artifact plus a small real scored cohort.
3. Publish one `gold_report_portfolio` release containing one model version.
4. Ask Lokesh to replace fixtures and reconcile one date's totals.
5. Ask Sujith to ingest one real scored event.
6. Ask Archi to trace one account from source features to score, explanation, and report.
7. Record G1 evidence. A fixture dashboard is not G1.

Do not train all accounts/dates simply to meet a scale claim. A bounded, disclosed demonstration with full historical source coverage is acceptable.

## November 1: release configuration

### S07: publish a versioned configuration

Persist:

- Release ID and source/feature versions.
- Selected model artifact URI/run ID.
- High/Medium thresholds selected by Irfan on validation.
- Reporting date range/cohort and account coverage.
- Replay account IDs and scenario ID.
- Approved business alert budget.

Publish only when all referenced assets exist. A failed new run must leave the prior release visibly dated, not masquerading as fresh output.

## November 2: actions and replay integration

### S08: persistent actions

Pair with Irfan and Sujith:

1. Derive first eligible threshold crossing for each account/scenario from the approved ordered score timeline.
2. Include prior state so replay starting above threshold has an explicit initial-state policy.
3. Calculate deterministic action ID from tenant/account/model/trigger snapshot.
4. Deduplicate the source action batch before Delta MERGE.
5. MERGE on action ID, inserting only absent actions. Do not reset a human-updated status to Open on re-run.
6. Preserve notification status separately. The job creating an action cannot claim Activator delivered a notification.
7. Expose action records to Lokesh.
8. Run the full replay and capture G2 evidence.

The action record may precede the replay notification because it is computed from historical scored state. Disclose that design. Do not call it a live CRM task unless an actual CRM integration exists.

## November 3: governance and recovery

### S09: prove implemented controls

- Check workspace membership and direct Lakehouse access.
- Confirm operational report tables contain no future-outcome columns.
- Review RLS tests with Lokesh; workspace editors bypass report RLS.
- Check no connection keys appear in notebook outputs or screenshots.
- Ask Ashish to run isolated invalid-input tests.
- Ask Irfan to prove feature/model mismatch fails visibly.
- Ask Sujith to show duplicate/restart behavior.
- Simulate a failed publication in a test item and verify it cannot replace the accepted release.
- Confirm timestamps show historical data freshness and current scoring execution separately.

Do not claim Purview, private networking, end-to-end exactly-once, or production compliance without implementation evidence.

## November 4: freeze

### S10: two clean runs

Use the same documented reset process twice:

1. Confirm capacity active and no competing heavy job.
2. Verify model/config versions.
3. Verify report as-of date and cohort.
4. Start bounded replay.
5. Observe event state, alert, action, and report.
6. Stop sender and deactivate idle streaming.
7. Check log/error outputs and cost.

Freeze schemas, model, thresholds, demo accounts, and report pages. Only defect fixes after this point.

## November 5-6: release and submit

### S11: export

Retain outside the expiring sandbox, in approved storage:

- Notebooks and dependency/runtime versions.
- Model artifacts, training feature list, metrics, and release config.
- KQL definitions, event mapping, rule settings, and replay instructions.
- Report exports/downloads where supported, screenshots, and recreation instructions.
- Semantic-model definitions where permitted; do not assume a Direct Lake report always downloads as PBIX.
- Architecture, synthetic-data statement, demo recording, and known limitations.

Open exported notebooks and check required assets exist. Remove secrets from exports.

### S12: submission

1. Confirm final required fields and file formats.
2. Ask Archi to sign off claims.
3. Run a small smoke test, not retraining.
4. Submit early and retain confirmation.
5. Coordinate final capacity pause/cleanup; do not delete the team's only remaining artifacts.

## Your daily cost checklist

- Actual and forecast spend checked; reporting delay understood.
- Capacity SKU unchanged.
- No duplicate resources.
- Spark sessions stopped when done.
- Eventstream/Activator not left running needlessly.
- Team informed before capacity pause.
- Remaining budget sufficient for rehearsal.

## Escalation

Use the sandbox support contact supplied by organizers. Send the exact error, resource/workspace, UTC time, and requested permission. Do not send passwords, connection strings, or tokens.
