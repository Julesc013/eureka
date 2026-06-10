# Artifact Evidence Returns

This directory holds deterministic fixtures for validating compact external
artifact evidence returns before they become manual observation or review input.

The fixtures are not external evidence. They are synthetic shape tests for the
return validator and intake rules.

## Current Examples

- `examples/valid_minimal_return/`: a valid compact return with one reviewable
  evidence target and one Windows 98 driver target that remains blocked for
  user details.
- `examples/invalid_verified_claim/`: an invalid return that attempts to claim
  a verified artifact.
- `examples/invalid_driver_missing_hardware/`: an invalid return that tries to
  move a Windows 98 driver target forward without hardware identity.

## Intake Boundary

A valid return may become reviewable input for:

```text
MANUAL-ARTIFACT-OBSERVATION-BATCH-03
```

It must not directly create:

- reviewed artifact records;
- verified artifacts;
- public index mutations;
- rights-clearance claims;
- malware-safety claims;
- download, install, or execution recommendations;
- public alpha readiness.
