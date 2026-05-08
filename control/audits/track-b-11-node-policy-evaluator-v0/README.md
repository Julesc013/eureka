# TRACK-B-11 Node Policy Evaluator

This audit pack records the first bounded Node Policy Evaluator for Track B.

## Added

- `runtime/local_foundry/node_policy_evaluator.py`
- `scripts/evaluate_node_policy.py`
- `scripts/validate_node_policy_evaluator.py`
- evaluator decision, reason, output, review, and runtime policy inventories
- committed evaluation examples under `examples/node_policy_evaluations/`
- generated sample evaluation report and summary under this audit pack
- documentation for reference, architecture, and review operations

## Why This Follows Dry-Run

The WorkUnit dry-run runner can simulate a WorkUnit without side effects. The
node policy evaluator checks whether a selected node manifest, policy, and
capability posture allow that dry-run, require review, or block the WorkUnit.
It prepares a policy decision layer without implementing node runtime behavior.

## What It Can Do

- Read explicit committed or temp-test node manifest, node policy, capability,
  and WorkUnit inputs.
- Compare node mode, capabilities, inputs, outputs, actions, source access,
  network/model/credential requirements, local state, and review gates.
- Produce a deterministic evaluation result and summary.
- Report `allowed_for_dry_run`, blocked, gated, deferred, or noop posture.

## What Remains Forbidden

- WorkUnit execution
- node runtime implementation
- local private state creation
- network, API, browser, model, provider, or live-source calls
- source sync, scraping, crawling, downloads, uploads, accounts, telemetry
- accepted evidence, accepted public records, or master-index mutation
- rights, malware-safety, installability, exhaustive-search, or
  production-readiness claims

## Next Task

TRACK-B-12 - Candidate store runtime.

