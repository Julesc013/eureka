# Validation

Planned validation lanes:

- JSON policy and inventory parsing
- `python scripts/eureka_lan_policy_check.py --host 127.0.0.1 --json`
- `python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --json`
- `python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --bind-lan --json`
- `python scripts/validate_local_lan_safety_gate.py`
- focused runtime and operations tests
- LOCAL validators
- generated artifact, architecture, and leakage gates

Full validation results are reflected in the final task report and commit body.
