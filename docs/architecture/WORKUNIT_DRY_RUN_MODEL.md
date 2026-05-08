# WorkUnit Dry-Run Model

The WorkUnit dry-run model sits between the WorkUnit contract and a future node
policy evaluator. It proves that a task can be inspected and converted into a
reviewable WorkUnitResult without enabling a real WorkUnit runtime.

## Flow

1. Load one explicit WorkUnit JSON file.
2. Validate contract vocabulary and required fields relevant to dry-run.
3. Evaluate required node modes and capabilities.
4. Evaluate source-access, network, model, credential, and local-state
   requirements.
5. Classify allowed actions as simulated, deferred, skipped, blocked, or
   not-applicable.
6. Record forbidden actions as `forbidden_checked`.
7. Build a WorkUnitResult with `executed_actions: []`.

The runner does not call providers, networks, live sources, browser automation,
or public search. It also does not create local private state. It is a simulator
for contract boundaries, not an executor.

## Action Classification

Dry-run classification uses this vocabulary:

- `allowed_for_dry_run`
- `simulated_only`
- `skipped_not_required`
- `blocked_by_policy`
- `forbidden_checked`
- `deferred_future`
- `not_applicable`
- `failed_validation`

Forbidden actions such as `mutate_master_index`, `mark_candidate_accepted`,
`enable_live_probe`, `scrape_external_site`, `download_binary`, `run_installer`,
`store_credentials`, `upload_to_hosted_backend`, and `emit_telemetry` are never
executed. They are only recorded as checked boundaries.

## Result Boundary

Every dry-run WorkUnitResult preserves false truth-boundary booleans:

- result is not observed baseline truth
- result is not accepted evidence
- result is not public truth
- result cannot mutate the master-index
- result cannot claim rights clearance, malware safety, verified
  installability, exhaustive global search, or production readiness

Review is required before any downstream use. The dry-run prepares later node
policy evaluator planning by making policy decisions explicit and replay-safe.
