import argparse
import getpass
import hashlib
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path


def load_events(path):
    with path.open(encoding="utf-8") as handle:
        events = [json.loads(line) for line in handle if line.strip()]

    if len(events) != 7:
        raise ValueError("Expected exactly seven setup events")
    if len({event["event_id"] for event in events}) != 7:
        raise ValueError("Event IDs must be unique")
    if len({event["object_id"] for event in events}) != 1:
        raise ValueError("Expected one replay object")
    for event in events:
        if event["account_id"] != "ACC008178":
            raise ValueError("Unexpected setup account")
        if event["replay_run_id"] != "schema_setup_001":
            raise ValueError("Unexpected setup replay run")
        if event["is_synthetic"] is not True:
            raise ValueError("Synthetic-data disclosure is required")
        if event["is_historical_replay"] is not True:
            raise ValueError("Historical-replay disclosure is required")
        if not 0 <= float(event["risk_score"]) <= 1:
            raise ValueError("Invalid risk score")
        datetime.fromisoformat(event["event_time"].replace("Z", "+00:00"))
        json.dumps(event, allow_nan=False)
    return sorted(events, key=lambda event: event["event_time"])


def select_alert_event(events, phase):
    date = "2025-07-15" if phase == "low" else "2025-08-01"
    selected = [
        dict(event) for event in events
        if event["event_time"] == date + "T00:00:00Z"
    ]
    if len(selected) != 1:
        raise ValueError(f"Expected one saved snapshot for {date}")
    event = selected[0]
    expected_band = "Low" if phase == "low" else "High"
    if event["risk_band"] != expected_band:
        raise ValueError(f"Saved snapshot is not {expected_band}")
    if (float(event["risk_score"]) >= 0.05) != (phase == "high"):
        raise ValueError("Saved score does not match the demo threshold")
    event["replay_run_id"] = "alert_demo_001"
    event["object_id"] = (
        f"{event['tenant_id']}|{event['account_id']}|alert_demo_001"
    )
    identity = json.dumps(
        [
            event["release_id"], event["replay_run_id"],
            event["tenant_id"], event["account_id"], event["event_time"],
        ],
        separators=(",", ":"),
    )
    event["event_id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Send seven saved model-score events to a Fabric custom endpoint."
    )
    parser.add_argument(
        "file", nargs="?", type=Path,
        default=Path(__file__).resolve().parent / "schema_setup_001.jsonl",
    )
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--alert-phase", choices=["low", "high"],
        help="Send one saved score as alert_demo_001. Verify low in Activator "
        "before sending high; the high phase can trigger configured notifications.",
    )
    args = parser.parse_args()
    events = load_events(args.file)
    if args.alert_phase:
        events = select_alert_event(events, args.alert_phase)
    print(f"Validated {len(events)} events from {args.file}", flush=True)
    print("Replay run:", events[0]["replay_run_id"])
    for event in events:
        print(event["event_time"], event["risk_score"], event["risk_band"])
    if args.validate_only:
        return

    try:
        from azure.eventhub import EventData, EventHubProducerClient, TransportType
        from websocket import WebSocket
    except ModuleNotFoundError:
        raise SystemExit(
            "Missing sender dependency. Run: "
            "python -m pip install azure-eventhub websocket-client"
        )

    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        connection_string = getpass.getpass(
            "Paste Event Hub connection string (hidden), then press Return: "
        ).strip()

    parts = dict(
        part.split("=", 1)
        for part in connection_string.split(";") if "=" in part
    )
    required = ("Endpoint", "SharedAccessKeyName", "SharedAccessKey")
    if any(not parts.get(key) for key in required):
        raise ValueError("Expected an Event Hub SAS connection string")
    entity = parts.get("EntityPath") or input(
        "Event Hub/entity name from Fabric source details: "
    ).strip()
    if not entity:
        raise ValueError("Event Hub/entity name is required")

    print("Connecting over secure WebSockets (port 443)...", flush=True)
    try:
        with EventHubProducerClient.from_connection_string(
            conn_str=connection_string,
            eventhub_name=entity,
            transport_type=TransportType.AmqpOverWebsocket,
            auth_timeout=30,
            socket_timeout=30,
            retry_total=0,
            logging_enable=False,
        ) as producer:
            batch = producer.create_batch(partition_key=events[0]["object_id"])
            for event in events:
                message = dict(event)
                message["emitted_at"] = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )
                encoded = EventData(json.dumps(message, allow_nan=False))
                encoded.content_type = "application/json"
                batch.add(encoded)
            producer.send_batch(batch, timeout=60)
    except Exception as exc:
        # SDK exception text may contain endpoint details; do not print credentials.
        print(
            f"Send did not complete successfully ({type(exc).__name__}). "
            "Delivery may be uncertain. Check Eventstream before retrying; "
            "a retry can create duplicate deliveries.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    print(f"Endpoint accepted the batch: {len(events)} events.")
    print("Replay run:", events[0]["replay_run_id"])
    print("Verify arrival in Eventhouse before resending.")
    print("Acceptance is not proof of ingestion or notification delivery.")
    if args.alert_phase:
        print("Configured alert rules may send notifications for this replay.")


if __name__ == "__main__":
    main()
