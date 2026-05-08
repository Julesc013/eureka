# TRACK-B-06 Validation

Validation is recorded after the Local Foundry State contract, examples,
validator, and tests are in place.

Required lanes:

- `git status --short`
- `git diff --check`
- JSON syntax checks for Local Foundry State inventories and audit report
- Track B node, policy, capability, WorkUnit, and WorkUnit result validators
- `python scripts/validate_local_foundry_state.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- Track A and OBS validators when present
- AIDE Lite doctor, validate, test, selftest, verify, eval, review-pack, and
  adapter validation lanes

No validation command in this pack performs observations, creates private local
state, calls networks, calls models/providers, or mutates product runtime
behavior.
