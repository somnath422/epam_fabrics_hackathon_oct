# Customer Intelligence Engine: judges' demo

**Target: 6-7 minutes** (judges' requested window: 5-10 minutes). One presenter. Use the editable deck plus the already captured Fabric screenshots/run evidence. The demo does not require sending new events during the presentation.

## Before recording

- Confirm tenant/workspace is available and current report/table values still match the evidence.
- Open the deck to slides 1, 3-4, 7-10, 11-15, 16, 18-20; do not present all 26 slides.
- Open Portfolio Overview, Account History, Retention Actions, Eventhouse event table, and the successful Activator run/task evidence in separate tabs.
- Keep backup screenshots/video available. Do not start a live replay unless the workspace owner has confirmed the connection, rule, budget, and no unintended notification recipients.
- Use the **synthetic and historical replay** disclosure before showing metrics.

## Run of show

### 0:00-0:45 — Problem and promise

> "Customer-success teams often see churn at renewal, after the opportunity to help has passed. Customer Intelligence Engine turns product, support, and engagement indicators into a prioritised, explainable review. Today we will show a working synthetic-data proof—not a production claim."

Point out in the architecture that there is a batch Lakehouse/model path and a separate **historical risk-score** replay/action path.

### 0:45-1:45 — Data and evidence

Show the model/test slide.

> "The data is seeded synthetic B2B SaaS, 10,000 accounts across a two-year date window. We held out both accounts and time. The 21,178-row test has 925 true positives and 10 false positives at a 0.05 High threshold: 98.93% precision, 81.43% recall, 0.8997 Spark area-under-PR."

Then disclose:

> "Because churn-positive snapshots are only 5.36% in this test, an always-negative model would already be 94.64% accurate. We report precision, recall, PR-AUC and account-level detection—not accuracy alone. Results are synthetic and not proof of production performance."

If asked about warning time:

> "Among 152 detected accounts, the first correct alert observed within the test window had a 54-day median lead, from 3 to 90 days. That is not a guaranteed 90-day warning and is not an account's lifetime-first alert."

### 1:45-3:00 — Portfolio and account review

Open Portfolio Overview with the September 30, 2025 date selected.

> "This page makes coverage explicit: 1,582 of 7,982 eligible accounts are scored, 19.82%. This is a bounded test/reporting cohort, not the whole eligible portfolio. There are 55 High, 5 Medium, and 1,522 Low."

Open Account History for `ACC008178`.

> "Here we inspect the selected account's score and available usage/support/engagement context. The driver contributions explain how this model score was assembled; they are associations in a synthetic dataset, not causal reasons."

Only describe fields and date ranges visible on screen. Do not claim a full two-year chart if the report view does not show it.

### 3:00-4:15 — Historical event path

Show the Eventhouse table or dashboard and the seven saved events.

> "These are seven saved model-score snapshots for one synthetic account, sent through the custom Eventstream endpoint into Eventhouse. They preserve historical event time and current replay time. This demonstrates the Fabric event ingestion path; it is not raw product-usage streaming or online inference."

Show July 15 score `0.015839` (Low) and August 1 score `0.103627` (High). The High threshold is `0.05`.

### 4:15-5:30 — Activator creates a review task

Show the successful `alert_demo_001` handler log and the Retention Actions row.

> "The event-level Activator rule invoked a validating notebook. It checked the replay, release, exact saved snapshot, score and High band, then created an insert-only retention task with an owner, evidence, and suggested play. We verified the task in Power BI."

Be explicit:

> "Notification status is 'Not attempted'. No email, Teams or CRM message was delivered. This is a durable human-review task, not autonomous customer outreach."

### 5:30-6:30 — Business value and future marketing strategy

> "The working value is a more focused, explainable queue for human review; no retained revenue or intervention uplift has been measured. Our next AI-assisted idea—suggested by our business analyst—is to use the account's supported risk drivers to draft retention-marketing options from approved playbooks. Usage decline might suggest an onboarding session; support friction might suggest coordinated service recovery. A CSM and Marketing must approve the audience, channel, and offer. We would measure incremental retention with a control before calling it effective."

Show the future Copilot slide and explicitly label it **concept, not built**. It should ground numeric answers in governed data, cite evidence, respect permissions, and abstain rather than "answer anything."

### 6:30-6:50 — Close

> "We have demonstrated a complete, inspectable path from a held-out risk score to a human-owned task. The next step is not to overclaim production readiness: it is to export the cloud assets, validate identity and governance, and test intervention value with an approved customer pilot."

## Likely questions

- **Is this production customer data?** No. It is generated synthetic data; the pre-churn degradation is intentionally designed into the generator.
- **Does the system guarantee three months' warning?** No. Target label is churn within 90 days; observed median warning among test detections is 54 days, minimum 3, with test-window censoring.
- **Is this SHAP?** No. It is signed coefficient contribution relative to training medians; the complete signed terms reconstruct the model score.
- **Is it streaming actual customer behavior?** No. Eventstream carried seven saved risk-score events in a historical replay.
- **Did Activator notify a CSM?** No. It created a task; notification was not attempted because the sandbox lacked supported mailbox/Teams delivery.
- **Can the Copilot create campaigns or answer anything?** Neither is built. The future proposal is bounded to approved playbooks and data, cites its evidence, respects consent/permissions, and requires human approval.
- **Is the model registered in Fabric ML, and is the report Direct Lake?** Those implementation details were not verified; do not claim either.
- **What about identity resolution, Fabric IQ, and Purview?** Not implemented/evidenced. This dataset has generated stable identifiers and is synthetic; it has no multi-source matching exercise or applied Purview labels.

## Backup behavior

If a live report or tenant page is slow, use the embedded dashboard screenshot, saved Eventhouse evidence, and successful Activator run/task screenshot. Do not send an event again simply because monitoring is slow; check the event/task first. Keep the synthetic-data and notification disclosures in the narration.
