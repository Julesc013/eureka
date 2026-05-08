# TRACK-B-01 - Eureka Node Manifest

This audit pack records the Track B contract-only node identity milestone.

## Added

- `contracts/node/eureka_node_manifest.v0.json` defines the node manifest shape.
- Node policy, mode, and capability registries live under `control/inventory/nodes/`.
- Six example manifests cover current local examples and future community, institution, and hosted worker modes.
- `scripts/validate_eureka_node_manifest.py` and `tests/contracts/test_eureka_node_manifest.py` validate the contract boundary.

## Why Track B Starts Here

Track B needs a governed node identity before node policy, WorkUnit execution, pack drafting, review, or runtime work can safely begin. This manifest defines what a node may discover, prepare, and propose while preserving the truth boundary.

Node output can become local candidates, source leads, evidence drafts, contribution pack drafts, review items, or future WorkUnit results. Node output cannot become accepted public truth, accepted evidence, rights clearance, malware safety, verified installability, or master-index mutation without later explicit review and promotion.

## Boundaries Preserved

- No node runtime was implemented.
- No local state was created.
- No network, browser, API, model, or provider access was enabled.
- No observations were performed or marked observed.
- No pack import, upload, hosted submission, review runtime, source sync, live probe, download, installer, account, or telemetry path was enabled.

## Validation

Run:

```text
python -m json.tool control/inventory/nodes/eureka_node_manifest_policy.json
python -m json.tool control/inventory/nodes/node_mode_registry.json
python -m json.tool control/inventory/nodes/node_capability_registry.json
python -m json.tool control/audits/track-b-01-eureka-node-manifest-v0/track_b_01_report.json
python scripts/validate_eureka_node_manifest.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

Track A and OBS validators remain compatible with this contract-only addition.

## Deferred

- TRACK-B-02 will define node policy.
- WorkUnit runtime, node local state, pack import/export behavior, source access, hosted workers, and master-index mutation remain future review-gated work.
