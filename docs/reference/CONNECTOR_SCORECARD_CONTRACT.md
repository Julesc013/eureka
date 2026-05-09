# Connector Scorecard Contract

Connector scorecards summarize fixture replay, policy evaluation,
live-probe-envelope posture, output-envelope validation, review integration,
quality delta, postmortem, coverage, and source-pack readiness.

Scorecards are operational evidence, not source truth. They do not claim
production readiness, automatically approve future connectors, grant live
access, mutate indexes, or accept evidence/candidates.

Validate with:

```powershell
python scripts/score_connector.py --input examples/connectors/core/scorecards/internet_archive_scorecard_v0.json --check
```
