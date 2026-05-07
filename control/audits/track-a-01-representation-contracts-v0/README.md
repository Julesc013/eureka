# TRACK-A-01 Representation Contracts v0

Track A-01 adds the first host/profile/representation contract bundle for
Eureka. It defines how host aliases, representation profiles, and capability
negotiation select compatible projections without changing resolver truth,
route meaning, source evidence, status, rights, risk, limitations, or action
posture.

## What Was Added

- Host profile schema, reference doc, inventory, example, and validation.
- Representation profile schema, reference doc, inventory, example, and
  validation.
- Capability negotiation schema, reference doc, policy inventory, example, and
  validation.
- Contract tests for valid inventories and required failure cases.
- A narrow repository layout validator update so AIDE forbidden-path metadata
  does not count as active legacy layout usage during full test discovery.

## Why This Supports Track A

Track A needs one stable projection vocabulary before public web, lite, text,
file-tree, API-like JSON, future snapshot, future relay, and future native
client work widens. This bundle makes host/profile selection explicit while
preserving the doctrine: one resolver truth, one route meaning, and many
compatible projections.

## Deferred

- Semantic renderer parity details remain for TRACK-A-02.
- Runtime renderer changes remain deferred.
- Hosted backend, DNS, custom domains, live probes, source connectors, native
  projects, snapshots, relay runtime, accounts, uploads, downloads, installers,
  execution, telemetry, and product search changes remain deferred.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/host_profiles.json`
- `python -m json.tool control/inventory/publication/representation_profiles.json`
- `python -m json.tool control/inventory/publication/capability_negotiation_policy.json`
- `python -m json.tool control/audits/track-a-01-representation-contracts-v0/track_a_01_report.json`
- `python scripts/validate_representation_contracts.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval list`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py adapter validate`

See `validation.md` for observed results.

## No-Goals

- No Eureka product runtime changes.
- No hosted backend claim.
- No deployment, DNS, CNAME, or custom-domain changes.
- No public route activation.
- No live probes or source connectors.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No master-index mutation.
- No native project creation.
- No broad docs rewrite.
- No generated site artifact mutation.

## Next Task Recommendation

TRACK-A-02 - Semantic renderer parity contract.
