# Smoke Matrix

PLAY-01 smoke validates:

- dry-run play session
- apply play session against a temporary initialized instance
- known hit query
- known local absence
- demo SearchNeed visibility
- demo WorkUnit visibility
- policy-blocked source probe WorkUnit
- policy-blocked extraction WorkUnit
- policy-blocked AI WorkUnit
- no source probes, extraction, model/provider calls, downloads, deployment, or
  public readiness claims

The operator instance supplied to the smoke command is not mutated.
