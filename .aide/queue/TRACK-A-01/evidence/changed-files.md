# TRACK-A-01 Changed Files

## Contract Bundle

- `contracts/representation/host_profile.v0.json`
- `contracts/representation/representation_profile.v0.json`
- `contracts/representation/capability_negotiation.v0.json`
- `docs/reference/HOST_PROFILE_CONTRACT.md`
- `docs/reference/REPRESENTATION_PROFILE_CONTRACT.md`
- `docs/reference/CAPABILITY_NEGOTIATION_CONTRACT.md`
- `control/inventory/publication/host_profiles.json`
- `control/inventory/publication/representation_profiles.json`
- `control/inventory/publication/capability_negotiation_policy.json`
- `examples/representations/host_profiles/minimal_host_profiles_v0.json`
- `examples/representations/representation_profiles/minimal_representation_profiles_v0.json`
- `examples/representations/capability_negotiation/minimal_capability_negotiation_v0.json`
- `scripts/validate_representation_contracts.py`
- `tests/contracts/__init__.py`
- `tests/contracts/test_representation_contracts.py`
- `control/audits/track-a-01-representation-contracts-v0/README.md`
- `control/audits/track-a-01-representation-contracts-v0/track_a_01_report.json`
- `control/audits/track-a-01-representation-contracts-v0/validation.md`

## Validation Guard Alignment

- `scripts/validate_repository_layout.py`

The repository layout validator change is limited to ignoring AIDE context and
queue metadata plus explicit forbidden-path references when scanning for active
legacy layout references. It does not change product behavior.

## AIDE Evidence

- `.aide/queue/TRACK-A-01/status.yaml`
- `.aide/queue/TRACK-A-01/evidence/changed-files.md`
- `.aide/queue/TRACK-A-01/evidence/validation.md`
- `.aide/queue/TRACK-A-01/evidence/track-a-contract-result.md`
- `.aide/queue/TRACK-A-01/evidence/remaining-risks.md`
