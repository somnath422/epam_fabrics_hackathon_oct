# Sujith: historical replay, Eventstream, Eventhouse, and activation

[Handbook](./README.md) | [Daily board](./01_Day_by_Day_Plan.md) | [Event contract](./02_Shared_Contracts_and_Acceptance.md)

You are Developer 4. Your goal is a real scored state -> event -> rule -> notification demonstration with explicit limits and measured duplicate behavior.

## Before starting

- Somnath supplies named workspace access and approves resource creation.
- Irfan supplies scored records; you do not invent risk trajectories.
- Ask Archi for a consenting internal notification recipient.
- Use one bounded replay cohort and one configured route initially.
- Do not create a separate Azure Event Hubs namespace just because an SDK is named Event Hubs. Fabric's custom endpoint can expose a compatible protocol.
- Do not assume a connection string is an HTTP URL.

## October 29: capability spike before committing

### R01: verify access

1. Fabric workspace -> New item.
2. Check whether Eventstream, Eventhouse, and Activator are available.
3. Create `es_customer_risk` only on the approved capacity.
4. Check whether a custom endpoint/custom app source is exposed.
5. Check Activator source/destination options and email/Teams actions.
6. Verify Teams/email policy using one explicit test recipient.
7. Record unsupported features immediately; ask Somnath for help instead of buying another resource.

Use official docs for the actual UI:

- [Custom source endpoint](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/add-source-custom-app)
- [Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction)

### R02: fixture

Use the flat fixture in [contracts](./02_Shared_Contracts_and_Acceptance.md). Label the item and event `is_fixture=true`. A successful fixture proves transport/configuration only.

## October 30: sender and storage

### R03: Eventstream -> Eventhouse

1. Workspace -> New item -> Eventhouse -> `eh_customer_intelligence`.
2. Open/create its KQL database -> `kql_customer_risk`.
3. Open `es_customer_risk` in edit mode.
4. Add custom endpoint/custom app source.
5. Inspect the protocol choices and sample producer code exposed by this source.
6. Secure the provided credential through the approved secret mechanism; do not paste it into committed code.
7. Add an Eventhouse destination to the stream.
8. Select database and create table `RiskEvents`.
9. Map JSON fields explicitly:

| Field | KQL type |
|---|---|
| event_id, replay_run_id, object_id | string |
| tenant_id, account_id, model_version | string |
| event_time, emitted_at | datetime |
| risk_score, arr_usd | real |
| top_driver_1, recommended_play, action_id | string |
| is_fixture | bool |

10. Publish/start the Eventstream according to the UI.
11. Send one fixture.
12. Confirm it appears in source preview and the destination query.

Do not manually create a table with a schema that conflicts with the destination mapping.

### Producer implementation

Use the protocol the endpoint actually offers:

- Event Hubs-compatible endpoint: use the provided Event Hubs connection parameters and compatible SDK.
- Kafka endpoint: use the displayed Kafka producer configuration.
- Other protocol: follow the generated source instructions.

For an Event Hubs-compatible source, a minimal sender function can look like this. It assumes `connection_string` and `entity_name` have already been retrieved securely from the actual source configuration:

```python
import json
from azure.eventhub import EventData, EventHubProducerClient

def send_events(connection_string, entity_name, records):
    with EventHubProducerClient.from_connection_string(
        conn_str=connection_string,
        eventhub_name=entity_name,
    ) as producer:
        for record in records:
            batch = producer.create_batch()
            batch.add(EventData(json.dumps(record, allow_nan=False)))
            producer.send_batch(batch)
```

If the connection string already includes EntityPath, follow the endpoint's generated sample for whether to pass `eventhub_name`; do not invent an entity name.

Only add/install `azure-eventhub` after the dependency is required and missing in the chosen environment. Never print the connection string.

Small demo sends can be one event at a time; large production traffic needs batching, retries, backpressure, and operational monitoring.

### R04: useful KQL

Run in the KQL database query editor:

```kusto
RiskEvents
| summarize Rows=count(), First=min(event_time), Last=max(event_time)
    by replay_run_id
```

Latest unique historical state:

```kusto
RiskEvents
| summarize arg_max(emitted_at, *) by event_id, replay_run_id
| summarize arg_max(event_time, *) by tenant_id, account_id, replay_run_id
| project tenant_id, account_id, replay_run_id, event_time,
          risk_score, top_driver_1, model_version
```

Timeline, replacing the example run/account:

```kusto
RiskEvents
| where replay_run_id == "rehearsal-001"
| where account_id == "ACC000001"
| summarize arg_max(emitted_at, *) by event_id
| project event_time, risk_score
| order by event_time asc
| render timechart
```

Repeated event visibility:

```kusto
RiskEvents
| summarize Copies=count() by replay_run_id, event_id
| where Copies > 1
```

Eventhouse accepts duplicates. A deduplicated query does not guarantee Activator received only one event.

## October 31: consume real model output

### R05

Ask Irfan for:

- Approved model version and frozen release ID.
- Flat scored records and actual drivers.
- Historical date range and cohort.
- Thresholds and scenario policy.
- At least one ordered account trajectory.

Replace fixture input. Preserve `is_fixture=false`. Do not remove historical date fields to make the stream look current.

## November 1: activation and timestamp semantics

### R06: wire the supported Activator path

Preferred simple topology:

```text
Scored event -> Eventstream -> Eventhouse
                           -> Activator destination/source
```

This avoids assuming every arbitrary Eventhouse query is an Activator source.

1. Open the stream; add an Activator destination if supported, or use Activator's supported eventstream connection.
2. Map `object_id` as the monitored object identity.
3. Map `risk_score` as the monitored numeric property.
4. For accelerated replay, use current `emitted_at` as the rule's processing timestamp where the source asks for a timestamp.
5. Keep historical `event_time` as an attribute and in Eventhouse.
6. Start with a low score then a high score from the same object.
7. Create rule using the actual validation-selected threshold from Irfan.
8. Prefer transition behavior ("becomes greater than/equal") if available, not an alert on every above-threshold event.
9. Test the rule against sample data, then enable it deliberately.

If the tenant's available route differs, verify it in the current UI and document the working connection. Do not claim Eventhouse-driven activation if the route is actually Eventstream-driven.

### R07: configure one delivery channel

Use built-in email or Teams only if the sandbox policy supports it.

Message content:

```text
Customer Intelligence Engine - historical replay
Account / tenant:
Snapshot date:
Risk score and model version:
Main driver:
Recommended play:
Assigned owner:
Action ID:
```

1. Send only to the approved internal recipient.
2. Confirm rule evaluation separately from notification acceptance.
3. Capture the received message if permitted.
4. Record processing latency using current send/receipt timestamps.
5. Do not use historical `event_time` to calculate transport latency.

External CRM integration and reliable per-message delivery receipts are not automatically provided by a built-in notification.

### R08: duplicate and cooldown policy

Implement layered protection:

1. Stable `event_id` for source retries.
2. Ordered source manifest plus a persisted progress checkpoint.
3. Rule transition/repeat settings actually supported by the tenant.
4. Idempotent action MERGE owned by Somnath.
5. A replay run ID that is reused on restart; use a new ID only for a deliberate new rehearsal.

Checkpointing has a send/checkpoint crash window. Do not claim exactly-once transport.

For business actions, deterministic action IDs prevent duplicate inserts even after restart. For notifications, measure whether the chosen rule/channel duplicates under repeated messages. If exact suppression cannot be guaranteed, disclose at-least-once behavior and avoid repeated sends during the pitch.

Do not claim "one alert" merely because the database contains one action.

## November 2: bounded replay

### R09: implement `06_replay_scored_events`

Sender behavior:

1. Read the approved bounded scored cohort, not 6.67M raw snapshots.
2. Filter one model version and accepted release.
3. Sort by historical event time and account ID.
4. Validate score range, required fields, finite numbers, and fixture flag.
5. Assign stable IDs.
6. Emit records at an adjustable interval, e.g. one historical day every one or two seconds for a short account sequence.
7. Support a start date and maximum event count so a mistake cannot send the full history.
8. Preserve checkpoint state in an approved durable location.
9. On errors, stop visibly and record failure; do not skip failed records silently.
10. Close the producer at completion.

For a five-minute pitch, do not replay 120 days at two seconds per day if other scenes need time. Start at an agreed historical point and show a small representative interval. Cohort-wide lead time still comes from the full evaluation.

Coordinate:

- Somnath has published the persistent action.
- Lokesh has the matching account/date and refresh instructions.
- Archi knows when to switch from account history to actual alert.

Capture G2: sender event -> Eventhouse record -> rule evaluation -> notification -> action record. Record which steps are historical/precomputed.

## November 3: failure and restart tests

### R10

| Test | Required observation |
|---|---|
| Same event sent twice | Action count unchanged; notification behavior recorded |
| Sender restart with same run ID | Progress resumes under documented policy |
| New deliberate run ID | New rule object state, but no accidental duplicate business action |
| Out-of-order old event | Does not silently reset accepted latest state/action policy |
| Invalid score / NaN | Rejected before send with visible error |
| Expired credential | Sender fails visibly; no "success" message |
| Notification blocked | Action can remain, delivery marked failed/unknown, limitation visible |
| Stable account | No false claim that every account should trigger |

If native rule state cannot handle out-of-order input, enforce ordered replay and explicitly limit that claim. Production would need stronger event-time handling.

## November 4: freeze and reset procedure

### R11

1. Freeze endpoint mapping, rule settings, model version, and replay manifest.
2. Write the exact reset sequence for a new intentional rehearsal.
3. Reuse IDs for retries; use a new run ID for a new isolated rule scenario.
4. Keep business-action IDs stable unless the scenario itself deliberately changes.
5. Run twice with Somnath and retain evidence.
6. Stop sender, deactivate unnecessary rules/stream paths, and coordinate capacity pause.

## November 5-6: export and demonstrate

### R12

- Export sender code without credentials.
- Retain KQL definitions, mapping screenshots, rule configuration, reset instructions, and test evidence.
- Record endpoint secret references, not secret values.
- Demonstrate actual delivery once during final rehearsal.
- Keep a recording if network/tenant availability fails.
- Do not leave an unbounded replay or active idle resource after the team is done.

## Explicit fallback ladder

1. **Full path:** Eventstream + Eventhouse + Activator + real notification.
2. **Delivery blocked:** real rule evaluation + persistent action queue; external notification explicitly not implemented.
3. **Activator unavailable:** a scheduled/notebook threshold job creates actions; show it as batch activation, not Activator.
4. **Streaming unavailable:** replay scored history in the report/KQL where possible; disclose real-time integration missing.

Fallbacks keep a useful solution, but do not count as completion of a blocked capability.
