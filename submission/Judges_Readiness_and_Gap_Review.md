# Judges' readiness and capability gap review

Reviewed November 10, 2026 against the judging slide supplied by the team and the recorded implementation in [PROJECT_MEMORY.md](../PROJECT_MEMORY.md). This is an evidence-based review, not a live tenant inspection or a score prediction.

## Executive assessment

The solution is **not feature-complete against the seven-item target**. Its strongest defensible entry is a working, explainable, synthetic-data decision loop: Lakehouse data foundation, disjoint held-out test, persisted risk contributions, Power BI, historical scored-event ingestion, and an Activator-triggered retention task. It now also has a user-verified six-entity ontology with OneLake bindings and successful Ontology Agent queries in Fabric's Preview experience. Real entity matching, KQL-derived journey signals, a Copilot Studio agent, Purview labels, and verified Direct Lake mode remain incomplete or unverified.

Do not promise to win or imply that breadth alone wins. The rubric assigns 50/100 points to Business Value and Solution Quality, 20 to Technical Excellence, and 30 to Innovation plus Presentation & demo. A truthful, reliable, rehearsed 5-10 minute proof is a better use of remaining effort than presenting unbuilt enterprise components as implemented.

## Requested capability audit

| # | Requirement | Status | What evidence supports | What remains / safe wording |
|---|---|---|---|---|
| 1 | Resolved Customer 360 Gold table, documented identity rules, match-quality report | **Partial** | `gold_customer360_daily` is a typed account-day Gold feature table; Silver account/contact/subscription/usage/support/interaction/outcome tables were joined on generated stable identifiers. | This is a one-source conformed profile, **not** multi-source identity resolution. No deduplication/cross-source match policy or precision/recall/ambiguous-match quality report was evidenced. Call it a Customer 360 feature table, not a resolved master identity. |
| 2 | Published Fabric IQ ontology with entities bound to OneLake | **Implemented in Fabric Ontology Preview; export/persistence still to verify** | User created `ont_customer_intelligence`, with six entity types, five Account relationships, OneLake bindings, composite keys, metadata, loaded instances, and successful Ontology Agent queries for related Contact and UsageObservation records. | The UI identifies the experience as Preview. Export its definition and retain evidence. This ontology is not cross-system identity resolution; generated IDs and a single synthetic source provide no match-quality report. Do not call the Ontology Agent preview a Copilot Studio deployment. |
| 3 | Eventstream-to-Eventhouse plus KQL journeys and 3 longitudinal behavior signals | **Partial** | Eventstream custom endpoint and Eventhouse/KQL destination were configured; seven saved historical **risk-score** events were observed in the table. | This is a historical score-state replay, not a raw usage-event stream. No saved KQL journey query or three Eventhouse-derived behavioral signals were evidenced. Usage/trend features exist in batch Gold/model inputs, not as three validated KQL event signals. |
| 4 | Scheduled dynamic segmentation, membership auditable over time | **Partial** | Risk/segment output is present in historical scored account rows; the segment is rule-based from the strongest model contribution. | It is not a validated customer segmentation taxonomy. A scheduled pipeline, segment definition/version history, and a complete membership-change audit were not demonstrated. Daily snapshots apply only to the scored cohort. |
| 5 | Registered Fabric ML churn model; held-out accuracy, precision/recall, lift; per-account attributions | **Partial** | A Spark logistic-regression pipeline was saved at `Files/models/churn_lr_v1`; a disjoint held-out test was evaluated. Full signed per-feature contributions reconstruct every test score. | Fabric ML registry registration is not evidenced. Precision/recall/F1/PR-AUC and confusion matrix are recorded; accuracy and lift were not recorded as report metrics. They can be derived from the confusion matrix below, with imbalance caveats. Contributions are coefficient-based, not SHAP. |
| 6 | Activator + Copilot Studio agent delivers scored, explained action brief | **Partial** | An event-level Activator rule invoked a validating notebook handler; one event created an auditable retention task containing account, score context, driver/play, owner/status. | No Copilot Studio agent exists. No email/Teams/CRM notification was delivered (`Notification status: Not attempted`). This is an Activator-to-notebook task workflow, not a multi-agent system or delivered Copilot brief. |
| 7 | Power BI Direct Lake 90-day risk dashboard; Purview labels on all personal data | **Partial / unverified** | Three-page Power BI report shows risk, history, and tasks; target is churn within 90 days. September 30 page shows scored-cohort coverage. | Direct Lake storage mode was not verified. No Purview sensitivity labels on personal/contact fields were evidenced. The data is synthetic, but that does not establish governance controls. Do not claim either feature until captured in Fabric/Purview. |

### Requested evaluation metrics, derived carefully

Recorded untouched test confusion matrix at High threshold `0.05`:

| TP | FP | FN | TN | Test snapshots |
|---:|---:|---:|---:|---:|
| 925 | 10 | 211 | 20,032 | 21,178 |

Derived from those counts (not a separately persisted evaluator metric):

- Accuracy = `(TP + TN) / N` = **98.96%**.
- Test positive prevalence = `(TP + FN) / N` = **5.36%**.
- Precision = **98.93%**; lift over test prevalence = `precision / prevalence` = **18.44x**.
- Recall = **81.43%**; F1 = **89.33%**; Spark `areaUnderPR` = **0.8997**.

Always display the majority-class baseline: predicting every snapshot negative would already be **94.64% accurate**. Accuracy alone is therefore a poor headline. Explain that repeated account-day rows are not independent; report the disjoint account cohorts and the separate unique-account detection result too. Do not label PR-AUC as average precision.

## Fit to the judges' 100-point rubric

| Category | Weight | Defensible strengths | Main risk to score | Best remaining preparation |
|---|---:|---|---|---|
| Business value | 25 | Specific retention prioritisation problem, account explanation, human-reviewed task; the business analyst's risk-based marketing strategy idea creates a clear next-value hypothesis. | No real customer validation, saved revenue, measured intervention effect, or real data; ARR x score is only a prioritisation proxy. AI-generated campaigns are not implemented. | Present strategy suggestions as future scope: approved playbook, evidence + audience + assumptions, CSM/Marketing sign-off, then controlled uplift measurement. |
| Technical Excellence | 20 | Fabric Lakehouse medallion path, leakage-aware split, explicit features, evaluation, signed explanations, Ontology Preview, Eventstream/Eventhouse, Activator handler. | Synthetic source flaws; incomplete deployment exports; no proven identity resolution, KQL journeys, registry, Purview, or verified Direct Lake. | Demonstrate a reproducible architecture and precise boundaries; export notebooks/model/report definitions and ontology; show safeguards and gaps as roadmap, not claims. |
| Solution Quality | 25 | Actual score -> event -> Activator -> persisted task -> report loop; retry/status preservation and score reconstruction were checked. | No end-user notification; limited historical scoring coverage; startup delay; cloud source artifacts not yet in Git; live tenant state not rechecked. | Rehearse the same bounded path, verify all screens before pitch, record a backup, and explicitly show the task is created (not email delivered). |
| Innovation | 15 | Combines early-warning modelling, a working Ontology Preview with related OneLake entities, and an inspectable event-to-task loop with human review. Risk-based retention-marketing suggestions are a proposed extension, not built. | Synthetic historical score replay is not live event inference; no production agent or multi-source matching. | Show the grounded Copilot plus approved-playbook idea as next phase only; require evidence and CSM/Marketing approval, not automatic outreach. |
| Presentation & demo | 15 | Editable visual deck, presenter notes, Power BI evidence, clear synthetic disclosure. | Prior script/architecture had unsupported claims; 26 slides are too many to present linearly in 5-10 minutes. | Use the corrected 6-7 minute script; select 5-7 slides; demo one verified path; use screenshots/logs if tenant latency blocks. |

These are readiness observations, not numeric scores awarded by judges. The supplied rubric asks whether it works and could be used for a customer opportunity; a credible working slice and honest limitations are persuasive evidence.

### Ontology verification update — November 10

The user configured `ont_customer_intelligence` in the Fabric Ontology Preview experience: six entities and five Account relationships, bound to the `silver_*` OneLake/Lakehouse sources with composite keys and descriptions. The Ontology Agent successfully returned the related Contact for `TEN007965` / `ACC007965`, and the three most recent related UsageObservation rows (Dec 28-30, 2025). The full entity/key/source inventory is in [PROJECT_MEMORY.md](../PROJECT_MEMORY.md). This is evidence for ontology exploration and relationships, not identity match quality, production Copilot Studio, or version-controlled deployment. Export the ontology definition before closing the capability.

## Priority before submission

1. **P0 — stop overclaiming:** use the corrected [submission statement](./Submission_Form_Content.md), [demo script](./Demo_Script.md), and [architecture](./Customer_Intelligence_Engine_Architecture.svg). Remove SHAP, MLflow registry, live usage stream, CRM/email delivery, full-portfolio coverage, Direct Lake, and Purview claims unless the team captures new proof. The ontology is now demonstrated in Preview; preserve its export and label its Preview status.
2. **P0 — make the five-to-ten-minute demo deterministic:** show portfolio date + coverage, one account explanation, seven saved risk snapshots or Eventhouse rows, Activator run evidence, and the persisted task. Have screenshots/video ready; no live sender is required.
3. **P1 — improve reproducibility/evidence:** export sanitized Fabric notebooks, model metadata, DAX/report definitions, KQL mappings, Activator configuration, evaluation tables, run/task evidence. The repo currently does not reproduce the cloud deployment.
4. **P1 — add match audit only if there are multiple actual source identities:** state key-based joins for this generated dataset. Do not invent fuzzy matches or an impressive but meaningless match rate.
5. **P2 — pursue product extras only if access, time, and budget are confirmed:** KQL behavioral signal tables, scheduled/auditable segments, model registry, Copilot Studio with approved risk-based marketing playbooks, Direct Lake verification, and Purview classification require further build/evidence. Export the now-configured ontology first. Do not spend sandbox capacity or buy a license on assumption.

## Rehearsal acceptance checklist

- [ ] At least one presenter can explain the 90-day label, split, threshold, 54-day median lead, and synthetic limitations without reading.
- [ ] Screens agree on September 30, 2025, the 55/5/1,522 distribution, and 19.82% scored coverage of 7,982 eligible accounts.
- [ ] The event shown is explicitly historical **risk-score** replay; the August 1 score `0.1036268` exceeds the `0.05` High threshold.
- [ ] Activator output says `Created`; the task row is visible and `Notification status` is not misrepresented.
- [ ] No chart calls ARR-times-score expected loss or says a retention action saved revenue.
- [ ] Backup screenshots/video and slide selection are open before recording; total video is within organizers' 5-10 minute requirement.
- [ ] Confirm submission deadline, allowed video format, and tenant availability with organisers; the original local plan's dates may be stale.
