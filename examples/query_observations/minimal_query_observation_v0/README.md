# Minimal Query Observation v0

This directory contains a synthetic P59 query observation example for
`windows 7 apps`.

The example is not collected from a real user. It retains no raw query, includes
no private path, no credential, no account identifier, no IP address, and no
local identifier. It records summary-only result posture against the controlled
public index and keeps every mutation flag false.

Validate it with:

```bash
python scripts/validate_query_observation.py --observation-root examples/query_observations/minimal_query_observation_v0
python scripts/validate_query_observation.py --all-examples
```

`CHECKSUMS.SHA256` covers the committed example files and is checked by the
validator.
