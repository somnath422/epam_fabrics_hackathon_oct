# Daily execution board: October 29-November 6

[Handbook](./README.md) | [Contracts and acceptance](./02_Shared_Contracts_and_Acceptance.md)

All dates are 2026. Deadline and sandbox expiry must be confirmed. Allocate approximately four to six focused build hours per person per day; adjust capacity bookings to actual availability. Every task has one accountable owner.

**Named ownership:** Dev 1 = **Ashish**; Dev 2 = **Irfan**; Dev 3 = **Lokesh**; Dev 4 = **Sujith**. Somnath Roy leads; Archi S owns business analysis and acceptance. Developer numbers below are stable workstream IDs, not unassigned positions.

## Daily operating rhythm

- Start: 15-minute stand-up. Yesterday's evidence, today's output, dependencies, blockers.
- After stand-up: 20-minute producer/consumer pairing for schema or model changes.
- Work blocks: parallel authoring; booked heavy compute, not six simultaneous Spark jobs.
- Midday: 10-minute integration check. Escalate a blocker after 30 minutes of distinct attempts.
- End: 30-minute demonstration and handoff, plus spend/status update from Somnath.

Post this handoff:

```text
Task ID:
Item/table and version:
What changed:
Validation result:
Evidence location:
Next consumer:
Known limitations/blockers:
Next action and owner:
```

## October 29: access, contracts, and first fixtures

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S01 Verify capacity/credits/expiry; S02 assign names and named access; S03 create workspace/Lakehouse; S04 freeze v1 contracts | Workspace and resource inventory; permission matrix; gate dates |
| Archi | A01 confirm persona/problem; A02 assumptions and response SLA; A03 acceptance checklist | One-page business brief; claim/evidence register |
| Dev 1 | D01 inspect CSV; D02 upload; D03 ingestion notebook and source checks | Bronze file/table or explicit upload blocker |
| Dev 2 | M01 allowlist and split; M02 small development extract; inspect leakage | Reproducible split plan and feature list |
| Dev 3 | B01 learn report/model/measure concepts; B02 browser capability check; create fixture report | Saved report with a card, table, and slicer |
| Dev 4 | R01 Eventstream/Activator permissions and delivery spike; R02 fixture event mapping | One event visible or documented blocker/fallback |

**Gate G0:** All six can work without credentials sharing. Confirm no duplicate paid capacity. Fixtures carry an explicit label.

## October 30: trustworthy features and independent prototypes

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S05 review contracts; book compute; wire task order; check costs | Agreed dependencies and executable item list |
| Archi | A04 playbook and segments; A05 source-quality acceptance review | Approved definitions and issue decisions |
| Dev 1 | D04 typed Silver; D05 DQ failures; D06 trailing-window Gold features | Gold v1 plus DQ report |
| Dev 2 | M03 baseline; M04 logistic regression; M05 boosted model on bounded extract | MLflow experiments; preliminary validation only |
| Dev 3 | B03 semantic model; B04 portfolio/workbench layout on fixtures | Correct types and initial measures |
| Dev 4 | R03 sender -> Eventstream -> Eventhouse; R04 timestamp mapping | Ordered fixture timeline and KQL queries |

**Handoff:** Dev 1 supplies actual feature schema and a real small extract to Dev 2; Dev 2/4 agree scored-event format; Dev 3 gets stable report schema.

## October 31: first real batch integration

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S06 run preparation -> scoring -> publication; resolve cross-team defects | First integrated run ID |
| Archi | A06 check one account end-to-end and reconcile business totals | Signed G1 checklist |
| Dev 1 | D07 publish stable Gold and outcomes; optimize only measured bottlenecks | Versioned feature table |
| Dev 2 | M06 score real records; save model artifact and driver outputs | Risk table for a bounded date/cohort |
| Dev 3 | B05 replace fixtures with real reporting tables; reconcile cards | Real account score and explanation in report |
| Dev 4 | R05 consume real scored events; preserve event identity | At least one real scored event in Eventhouse |

**Gate G1:** Source -> historical features -> model -> risk table -> Power BI works. No invented probability or driver is used as evidence. If gate fails, cut stretch features immediately.

## November 1: evaluation, explanations, and decision usefulness

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S07 stabilize release config and run log; review leakage controls | Re-runnable release candidate |
| Archi | A07 independent metric/value review; A08 validate recommendations | Measured versus assumed claims separated |
| Dev 1 | D08 temporal boundary tests; cold-start and date-quality flags | Feature test evidence |
| Dev 2 | M07 freeze validation threshold; M08 test once; M09 SHAP and lead time | Evaluation tables and model card |
| Dev 3 | B06 account page; B07 segments/formatting; no double-counted ARR | Three usable report pages |
| Dev 4 | R06 threshold transition; R07 notification route; R08 duplicate strategy | Successful permitted test notification |

**Rule:** Do not adjust thresholds after looking at test results to improve the pitch. Any subsequent revision requires a new disclosed evaluation protocol.

## November 2: real-time integration

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S08 integrate action persistence; oversee full replay; check budget | G2 evidence and pipeline order |
| Archi | A09 choose primary/contrast accounts under declared criteria | Demo account selection record |
| Dev 1 | D09 publish bounded replay feature/history extract | Stable replay cohort |
| Dev 2 | M10 publish approved scored timeline/model version | Real score sequence with drivers |
| Dev 3 | B08 expose action queue and selected account; refresh instructions | Integrated retention workbench |
| Dev 4 | R09 replay real timeline; test duplicate delivery and restart | Eventhouse timeline + real alert + dedup evidence |

**Gate G2:** A scored historical state reaches the real-time stack and produces the expected alert. A persistent action exists. Separate evidence records whether the notification was accepted/delivered; do not infer delivery from the action row.

## November 3: governance, failure tests, and recovery

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S09 access review; pipeline failure/stale-run behavior; recovery run | Operational checklist |
| Archi | A10 execute acceptance suite; A11 verify tenant/security claims | Defect list with priorities |
| Dev 1 | D10 bad-key/date/missing-file tests in isolated fixtures | Checks fail visibly |
| Dev 2 | M11 missing-feature/version tests; calibration assessment | Model limits and failure evidence |
| Dev 3 | B09 RLS test; totals and historical filters; stale-score label | Authorized versus denied results |
| Dev 4 | R10 restart/out-of-order/cooldown tests; deactivate idle paths | Failure matrix and replay reset procedure |

Never corrupt production tables to run a negative test. Use isolated fixture tables/items.

## November 4: freeze and two clean runs

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S10 enforce freeze; run complete path twice; sign release | G3 pass/fail and known limitations |
| Archi | A12 final story and architecture addendum | Pitch outline backed by evidence |
| Dev 1 | D11 freeze feature schema; export notebooks | Reproducible data release |
| Dev 2 | M12 freeze model/threshold and evaluation artifacts | Reproducible scoring release |
| Dev 3 | B10 final visual polish and data verification | Stable report release |
| Dev 4 | R11 freeze event schema/rules; verify reset and stop | Stable real-time release |

**Gate G3:** Two clean runs without ad hoc table edits. Optional AI work is allowed only if G3 passes, access is already available, and it does not threaten time/budget.

## November 5: rehearse, record, export

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S11 validate exports and submission requirements; reserve resources | Release inventory and backup |
| Archi | A13 narrate/rehearse; A14 record backup and judge Q&A | Final video/script/evidence pack |
| Dev 1 | D12 verify clean-start instructions and source manifest | Data handover complete |
| Dev 2 | M13 verify model reload and identical score output within tolerance | ML handover complete |
| Dev 3 | B11 verify shared viewing/license; export permitted report assets | BI handover complete |
| Dev 4 | R12 final alert test; remove secrets from export; shut idle ingestion | Replay handover complete |

Do not depend on the sandbox still existing on showcase day. Ask organizers how to preserve or re-provision the demo.

## November 6: submission, not new development

| Owner | Tasks | End-of-day output |
|---|---|---|
| Somnath | S12 final smoke test, submit early, retain confirmation | Submitted package |
| Archi | A15 check all answers/claims/attachments | Final approval checklist |
| Dev 1 | Support source and reproducibility questions | No new feature changes |
| Dev 2 | Support evaluation questions | No retuning |
| Dev 3 | Open report as intended viewer and check filters | Working viewing path |
| Dev 4 | Check rehearsal alert destination and turn off unused paths | Controlled runtime |

## Critical dependencies

```text
S03 -> D02 -> D04 -> D06 -> M06 -> B05 -> G1
M07/M08/M09 -> M10 -> R09 -> G2
R01 can run on fixtures before M10
B01/B02/B03 can run on fixtures before M06
A01/A02/A03 and QA design can run independently
G1 + G2 + governance/failure tests -> G3 -> rehearsal -> submission
```

## Stop/go decisions

| Situation | Decision |
|---|---|
| Access/capacity blocked >30 minutes | Somnath escalates to sandbox support; other members continue fixtures/documented offline design |
| Browser upload repeatedly fails | Dev 1 splits source into header-preserving CSV parts; do not keep retrying a giant file |
| Model underperforms rule baseline | Disclose result; select the defensible simpler model, do not cherry-pick test data |
| Notification permissions absent | Persist action queue and demonstrate rule evaluation; explicitly disclose external delivery not implemented |
| Power BI browser editing blocked | Check permissions first; Windows Desktop fallback only if available, otherwise escalate |
| Report latency too high | Reduce reporting history/cohort, not business correctness; disclose scope |
| Spend unexpectedly rises | Stop optional/idle workloads; inspect cost and capacity metrics before resuming |
