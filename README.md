# Customer Intelligence Engine

Explainable B2B SaaS churn early warning and human-reviewed retention actions on Microsoft Fabric.

**Start with [PROJECT_MEMORY.md](./PROJECT_MEMORY.md)** for the implementation handoff, verified results, operating instructions, known gaps, and extension roadmap. Updated November 10, 2026.

## Repository map

- [Project memory and continuation guide](./PROJECT_MEMORY.md): current implementation, not just the original plan.
- [Team handbook](./build/README.md) and [shared contracts](./build/02_Shared_Contracts_and_Acceptance.md).
- [Fabric ingestion and Gold guide](./build/09_Setup_Ingestion_Gold_Guide.md).
- [Synthetic data generator](./generate_master_csv.py).
- [Local historical replay sender](./send_replay_events.py) and [seven saved model-score events](./schema_setup_001.jsonl).
- [Editable 26-slide judges' deck](./submission/Customer_Intelligence_Engine_Judges_Deck.pptx).
- [Original blueprint](./blueprint/Customer_Intelligence_Engine_Blueprint.md).

The demo uses synthetic data and historical replay, not live inference. A retention task was created automatically; email/Teams delivery was not demonstrated. The chatbot in the deck is a future concept, not an implemented feature.

The generated CSV is intentionally excluded from Git. Cloud notebooks, model artifacts, semantic model, reports, and streaming/Activator definitions still require export from Fabric before this repository can independently reproduce the complete deployment. See the [export checklist](./PROJECT_MEMORY.md#9-export-and-reproducibility-checklist).
