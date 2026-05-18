# Validation

Planned validation lanes:

- JSON syntax checks for PLAY-02 policy, inventories, and audit report
- `python scripts/validate_play_seed_pack.py`
- `python scripts/validate_play_session.py`
- `python scripts/validate_play_smoke_pack.py`
- temp-instance smoke with `--use-temp-instance --apply-demo-to-temp`
- dry-run smoke against `..\instances\default`
- focused PLAY seed/session/smoke tests
- architecture boundary and generated-artifact cleanliness checks
- AIDE doctor, validate, test, selftest, verify, review-pack, and commit check

Full discovery is optional for PLAY-02 because changes are focused on the local
PLAY smoke lane and existing broad-lane failures are tracked separately.
