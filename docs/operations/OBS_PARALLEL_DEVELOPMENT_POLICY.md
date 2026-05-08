# OBS Parallel Development Policy

Manual observation should calibrate Eureka, not stall all development.

Decision: Continue main development in parallel with OBS after OBS-REPLAN-01, unless a specific task depends on completed manual baseline evidence.

## Parallel Work Rules

- Track B work may continue after Track A and OBS replan.
- Manual Observation Batch 0 remains the human gold-standard lane.
- Agent-assisted observation candidates may run in parallel with Track B.
- OBS-LOCAL work may run without network access.
- The first live connector still requires explicit source approval.
- Observations may feed SearchNeed, WorkUnit, Candidate, or EvidencePack fixtures after review.
- Observations and candidates do not directly mutate the master index.
- Human approval remains required for evidence-quality and source-policy decisions.

## Stop Conditions

Stop if a task needs actual external evidence, source-policy approval, legal or privacy judgment, live connector authorization, production deployment, or irreversible master-index mutation.
