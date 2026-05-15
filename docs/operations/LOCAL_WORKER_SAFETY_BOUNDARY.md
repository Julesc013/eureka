# Local Worker Safety Boundary

LOCAL-09 enables deterministic local execution only. A worker run is a queue operation plus an auditable local result; it is not truth, evidence acceptance, source approval, rights clearance, malware safety, production readiness, or public launch readiness.

## Allowed Effects

- WorkUnit state transitions
- WorkUnit transition history
- worker result references
- worker audit references
- local public-index rebuild only for `reviewed_index_rebuild_worker` with an operator token

## Forbidden Effects

- source probes
- extraction
- AI/model/provider calls
- downloads
- installs
- executable actions
- source sync
- LAN operations
- deployment
- site/dist writes
- master-index mutation
- source registry mutation
- connector registry mutation

If a worker kind is not enabled in `local_worker_allowed_kinds_policy.json`, the runner blocks it before execution and records the policy decision.
