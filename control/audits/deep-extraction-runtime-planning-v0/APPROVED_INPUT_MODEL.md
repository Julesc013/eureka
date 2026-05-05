# Approved Input Model

Future allowed inputs:

- repo-local synthetic extraction examples
- fixture containers created specifically for tests
- operator-approved local fixture path after explicit approval
- reviewed pack-import dry-run output future
- reviewed source-cache candidate future
- reviewed object-page representation future

Forbidden inputs:

- arbitrary local paths
- arbitrary directories
- user-uploaded files
- URLs
- private cache roots
- connector live responses
- package-manager outputs
- executable installer paths
- raw telemetry
- private query observations

Rules:

- Inputs must be bounded, explicit, approved, and never supplied directly by
  public request parameters.
- Unknown inputs are rejected.
- P105 adds no input reader.

