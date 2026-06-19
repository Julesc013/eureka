# Source Foundry Preview v0 Drift Repair 01

Status: `BLOCKED_GENUINE_REGRESSION`

This packet records the first targeted repair pass after the Source Foundry
Preview v0 full-discovery drift triage.

The pass investigated the two unknown groups before historical drift repairs:

- `runtime_leakage_safety_unknown`
- `local_worker_validator_unknown_or_slow`

The local-worker group was reclassified as historical queue expectation drift:
worker behavior passed, but the validator still requires the old `LOCAL-09` to
`LOCAL-10` queue posture.

The runtime leakage group remains a blocker. The current runtime architecture
leakage gate reports 52 new unallowlisted production-path findings, including
36 blocker-severity findings. Runtime product paths are protected in this task,
so the repair must move to a separate runtime-leakage authority task before
another external full-discovery rerun is justified.

No full unittest discovery was run inside this session. No external rerun handoff
was prepared.

