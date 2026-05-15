# Validation

HUNT-04 validation completed on the local VS Code machine.

- PASS: JSON syntax for HUNT-04 policies, inventories, and audit report.
- PASS: `python scripts/validate_search_hunt_exhaustion.py`.
- PASS: focused exhaustion runtime, route, UI, auth, and script tests.
- PASS: ignored local-instance CLI smoke for init, validation, token setup, hunt creation, exhaustion generation/show, and demo.
- PASS: localhost service smoke for Hunt UI and local service routes.
- PASS: HUNT-01, HUNT-02, and HUNT-03 validators.
- WARN: HUNT-00 validator passes with inherited final-baseline warning disposition.
- WARN: LOCAL validators pass with inherited runtime leakage warning disposition.
- PASS: generated artifact cleanliness after committing intended audit/generated outputs.
- PASS: architecture boundaries.
- WARN: runtime architecture leakage validation passes with existing allowlisted findings and zero new unallowlisted findings.
- PASS: full unittest discovery after restoring legacy repo-health compatibility fields.
