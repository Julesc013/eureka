# Validation

Validation is performed by `scripts/validate_hunt_replay.py`, focused replay unit tests, JSON schema checks using `python -m json.tool`, and repository cleanliness checks. The validator creates a disposable local instance and exercises plan-only, replay-local, verify-existing, service routes, UI rendering, token rejection, and LAN rejection.
