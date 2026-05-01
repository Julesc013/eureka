# Query Observation Contract v0

Status: contract-only.

This contract has no telemetry runtime and no runtime persistence.

`contracts/query/query_observation.v0.json` defines the first Query
Intelligence Plane record. It captures a privacy-filtered summary of a search
interaction for future learning, with no runtime persistence, no telemetry
runtime, no public query logging, and no mutation of search or master indexes.

## Required Sections

- `raw_query_policy`: raw query retention default is `none`; public-safe
  examples retain no raw query and mark raw text unsafe to publish by default.
- `normalized_query`: lower-risk normalized terms and safe public terms after
  redaction.
- `query_fingerprint`: query fingerprint over the normalized basis, marked
  non-reversible. Example fingerprints are deterministic and include no salt
  value.
- `query_intent`: coarse intent such as `find_software_version`, `find_driver`,
  `find_inside_container_member`, `check_compatibility`, or `unknown`.
- `destination`: intended user destination, with download/install/emulation
  intents explicitly represented as detected-but-disabled.
- `detected_entities`: public-safe entities such as platform, version,
  artifact type, package name, or source family.
- `result_summary`: summary-only result posture, not a result cache.
- `checked_scope` and `index_refs`: what controlled indexes or summaries were
  checked, with live probes and external calls false.
- `privacy`: publication and aggregate eligibility after filtering.
- `retention_policy`: future policy description only.
- `probe_policy`: probe enqueueing is false in P59.
- `no_mutation_guarantees`: hard false fields for master index, local index,
  candidate index, result cache, miss ledger, probe enqueue, telemetry export,
  and external calls.

## Current Example

`examples/query_observations/minimal_query_observation_v0/` contains a
synthetic `windows 7 apps` observation. It is not from a real user, retains no
raw query, and records only summary posture against the controlled public index.

Validate examples with:

```bash
python scripts/validate_query_observation.py --all-examples
python scripts/validate_query_observation.py --all-examples --json
```

Validate the whole contract pack with:

```bash
python scripts/validate_query_observation_contract.py
python scripts/validate_query_observation_contract.py --json
```

## Runtime Boundary

Public search routes do not write query observations in P59. The dry-run helper
prints a candidate observation to stdout only and writes no files.
