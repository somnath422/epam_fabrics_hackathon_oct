# Archi S: business analysis, acceptance, and presentation

[Handbook](./README.md) | [Daily board](./01_Day_by_Day_Plan.md) | [Acceptance tests](./02_Shared_Contracts_and_Acceptance.md)

## Your responsibility

Ensure the solution solves a clear business problem and every claim is defensible. You own persona, decision rules, assumptions, acceptance, and judge-facing narrative. You do not need to train the model or become a Power BI developer.

## October 29: define the decision

### A01: write a short business brief

Fill these fields with Somnath:

```text
User: Customer Success Manager / Customer Success leader
Decision: Which accounts should be contacted next, and why?
Current problem: Usage/support/relationship evidence is disconnected.
Prediction: Cancellation within the next 90 days.
Action: Human-approved adoption, support, or relationship intervention.
Success evidence: Useful held-out alerts + measured lead time + working action loop.
Data boundary: Synthetic B2B SaaS daily snapshots; historical replay.
```

### A02: approve illustrative assumptions

Propose, then get agreement:

- Alert budget: for example, review the top 20 accounts per weekly scoring period.
- Response SLA: for example, owner reviews a new action within two working days.
- Initial notification recipient: consenting internal team member only.
- Human approval required for discounts and customer outreach.
- Intervention effectiveness is unknown; use labeled sensitivity scenarios, not a claimed save rate.

These are demo assumptions, not facts about a real customer.

### A03: create a claim/evidence register

Use an approved spreadsheet or issue board:

| Claim | Actual or assumed? | Evidence owner | Output needed | Status |
|---|---|---|---|---|
| 10,000 accounts | Expected source fact, pending check | Ashish | Fabric profile output | Pending |
| Better than baseline | Unknown until measured | Irfan | Held-out comparison | Pending |
| Alert arrives before churn | Unknown until measured | Irfan/Sujith | Dates and action evidence | Pending |
| Tenant isolation | Implemented only after test | Lokesh/Somnath | Viewer test | Pending |
| Protected ARR | Illustrative estimate | Archi | Formula and assumptions | Pending |

Never turn a pending claim into a slide headline.

## October 30: define segments and plays

### A04: approve the action playbook

Use [proposed shared segment rules](./02_Shared_Contracts_and_Acceptance.md), then review sample accounts with Irfan:

| Segment | Interpretation | Play | Owner |
|---|---|---|---|
| Adoption decline | Product value may not be realized | Adoption review and enablement | Assigned CSM |
| Support distress | Service friction may be damaging confidence | Support escalation and recovery plan | CSM + support |
| Relationship gap | Engagement/champion continuity may be weak | Sponsor/champion outreach | Assigned CSM |
| Mixed risk | Several kinds of evidence | Coordinated account review | CSM lead |
| Monitor | No agreed segment condition | Review context, no automatic concession | CSM |

Review language: "may indicate" is appropriate; "caused churn" is not established by SHAP.

### A05: accept data limitations

Ask Ashish:

- Are all keys and dates valid?
- Which subscription-derived features were excluded?
- Which metrics are approximate synthetic signals?
- What accounts/dates are omitted from scoring and why?

Record limits rather than asking the team to hide them.

## October 31: first user acceptance

### A06: inspect one real account

Ask Lokesh to share the report in the browser:

1. Open portfolio page.
2. Select exactly one historical date.
3. Pick one high-risk account.
4. Check its ARR and account metadata against the published table.
5. Ask Irfan where its probability and drivers came from.
6. Confirm the explanation includes actual feature values, not invented percentages.
7. Confirm a recommended play and owner are visible.
8. Confirm fixtures have been removed from accepted pages.

Pass G1 only if the account is backed by real generated data and real model output.

## November 1: metrics and value

### A07: review the model results

Ask Irfan to explain, in plain language:

- Precision: among alerts, how many were positive under the defined outcome?
- Recall: how many positive cases did we detect?
- PR-AUC: ranking quality relative to positive prevalence.
- Alert volume: how much work is created?
- Lead time: how long between first qualifying alert and actual cancellation?

Require sample sizes and a baseline on the same population. Distinguish account-level metrics from account-day metrics.

### A08: build an honest value model

For one selected date and one row per account:

```text
Risk-weighted ARR exposure = sum(ARR * calibrated churn probability)
Illustrative protected ARR = sum(ARR * churn probability * intervention effectiveness)
```

If probabilities are not calibrated, label exposure a prioritization proxy.

Show several assumed effectiveness scenarios, for example 5%, 10%, and 20%. Do not claim any is measured retention uplift. A real causal uplift claim requires intervention/control evidence.

Do not multiply daily snapshots of the same account into extra revenue.

## November 2: choose the demonstration accounts

### A09: select under declared criteria

With Irfan:

1. Choose from a declared held-out test/replay cohort.
2. Require sufficient history, valid feature state, and visible score evolution.
3. Prefer a detected churner with useful lead time and understandable drivers.
4. Choose a stable contrasting account using the same evaluation scope.
5. Record the selection rule and cohort size.

The demo account illustrates behavior; it does not replace cohort-wide evaluation. Do not tune the model to make a selected account look better.

## November 3: execute acceptance tests

### A10: business tests

- [ ] One date selected; counts and ARR reconcile.
- [ ] No future cancellation date appears in the operational account page.
- [ ] Empty filters show "no accounts," not misleading zero-risk success.
- [ ] Alert contains account, historical date, model, driver, owner, and play.
- [ ] Duplicate replay does not add another action.
- [ ] A stale or failed run remains visibly stale/failed.
- [ ] Action closure is not described as an account saved.

### A11: governance evidence

Observe, with the responsible developers:

- Viewer sees only authorized tenant rows.
- Editor/admin RLS bypass is explained.
- Direct Lakehouse access is separately controlled.
- Notifications/exports contain no secrets.
- Implemented controls and proposed production controls are separated.

Log defects with severity, reproduction steps, expected behavior, actual behavior, and owner.

## November 4: presentation and architecture addendum

### A12: create a concise narrative

Five-minute example, adjusted to official limits:

| Time | Show | Say |
|---|---|---|
| 0:00-0:35 | Problem and persona | "Which accounts need attention, why, and what should we do?" |
| 0:35-1:10 | Portfolio/workbench | Explain risk and revenue prioritization |
| 1:10-2:20 | Account timeline | Replay changing synthetic historical evidence |
| 2:20-3:05 | Alert and action | Show actual notification and persistent action |
| 3:05-3:45 | Evaluation | Measured baseline comparison and actual lead time |
| 3:45-4:20 | Contrast account | Show a measured counterexample, if available |
| 4:20-5:00 | Architecture/value | Explain controls, assumptions, and production path |

Opening disclosure:

> "This demonstration uses synthetic B2B SaaS history. We replay account states scored by our trained model to prove the data-to-decision-to-action workflow."

Architecture addendum must cover component choices, planned/implemented security, budget choices, business assumptions, and limitations.

## November 5: rehearse and record

### A13: rehearse with the real environment

1. Agree who clicks and who narrates.
2. Check selected dates/accounts before recording.
3. Do not wait on slow notebooks during the pitch; use the prepared release.
4. Rehearse a clean reset and an explicit switch to backup recording.
5. Time it twice and trim platform-tour details before trimming proof.

### A14: backup and judge questions

Record the working path and capture metric screenshots. Prepare short answers:

- Why synthetic? To demonstrate timestamped multi-signal workflow without exposing customer data.
- Does it prove production performance? No; real data validation is required.
- Is this live inference? Initially no; it is replay of model-scored historical states.
- Is 90-day warning guaranteed? No; actual lead-time distribution is reported.
- Why not a simple rule? Show identical-population baseline comparison.
- Does SHAP prove cause? No; it describes model contributions.
- Is ARR saved measured? No; value scenarios are explicitly assumed.
- What is implemented security? Show tested controls, not a product feature list.

## November 6: final sign-off

### A15

- [ ] Official submission requirements satisfied.
- [ ] Numbers match frozen evaluation artifacts.
- [ ] Synthetic/replay boundaries explicit.
- [ ] No unsupported live-scoring, uplift, delivery, or compliance claims.
- [ ] Backup recording and exports open.
- [ ] Known limitations included.
- [ ] Submission confirmation retained by Somnath.
