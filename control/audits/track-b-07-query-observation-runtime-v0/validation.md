# TRACK-B-07 Validation

Validation is recorded after the runtime, policies, examples, scripts, tests,
docs, and generated sample evidence are in place.

Required lanes:

- `git status --short`
- `git diff --check`
- JSON syntax checks for Query Observation runtime inventories and audit report
- Track B node, policy, capability, WorkUnit, WorkUnit result, and Local
  Foundry validators
- `python scripts/validate_query_observation_runtime.py`
- `python scripts/record_query_observation.py --input examples/query_observations/minimal_query_observation_v0.json --check`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- Track A and OBS validators when present
- AIDE Lite doctor, validate, test, selftest, verify, eval, review-pack, and
  adapter validation lanes

No validation command performs external observations, public telemetry, browser
automation, source calls, model/provider calls, private local-state writes, or
master-index mutation.
