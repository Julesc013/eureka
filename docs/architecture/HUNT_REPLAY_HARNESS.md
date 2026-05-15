# Hunt Replay Harness

The deterministic hunt replay harness records and replays local Search Hunt workflow state for audit and reproducibility. It builds a fixture from a local hunt, lists deterministic replay steps, records blocked future steps, runs local replay steps behind an operator-token gate, and stores a replay diff.

Replay modes:

- `plan_only`: builds a fixture and result preview without mutating state.
- `replay_local`: runs deterministic local replay steps and records a replay result.
- `verify_existing`: compares an existing local hunt against replay expectations without creating new workflow records.

Replay is not truth, evidence acceptance, source approval, rights clearance, malware safety, or global absence proof. Source probes, extraction, AI/model providers, browser research, artifact acquisition, artifact launch, master-index mutation, site output writes, and deployment remain disabled.

HUNT-11 may add a disabled-by-default AI escalation gate. SYN and F0 remain separate follow-up tracks.
