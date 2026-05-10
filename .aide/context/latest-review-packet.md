# AIDE Review Packet

## Review Objective

Review H2-BUNDLE-03 package registry metadata live-probe framework evidence and decide whether it is acceptable to proceed to H2-BUNDLE-04 review integration.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `control/audits/h2-bundle-03-package-live-probes-v0/h2_bundle_03_report.json`
- `control/audits/h2-bundle-03-package-live-probes-v0/validation.md`
- `control/audits/h2-bundle-03-package-live-probes-v0/live_probe_execution_report.md`
- `.aide/verification/review-decision-policy.yaml`

## Changed Files Summary

- Added H2 package live-probe contracts under `contracts/connectors/`.
- Added H2 live-probe policies under `control/inventory/connectors/`.
- Added fail-closed source wrappers under `runtime/connectors/h2_package_registries/`.
- Added CLI, validator, summary script, examples, docs, tests, and audit evidence.
- Updated AIDE queue/context handoff for H2-BUNDLE-04.

## Validation Summary

- H2 live-probe validator: PASS
- H2 live-probe CLI check: PASS, blocked offline, no network
- H2 live-probe tests: PASS
- Full unittest discover: PASS, 2948 tests
- Architecture boundaries: PASS
- Existing H2/H1/H0/core validators: PASS
- AIDE doctor/validate/test/selftest/eval/review-pack/adapter: PASS
- AIDE verify: WARN, diff-scope warnings only, 0 errors

## Token Summary

- latest task packet approx_tokens: 1077
- latest review packet approx_tokens: 650
- method: manual chars / 4 estimate
- budget_status: within_budget

## Risk Summary

- All H2 package live probes are blocked by missing source-specific approval; this is intentional fail-closed behavior.
- H2-BUNDLE-04 should use fixture-equivalent and blocked-output evidence unless a future operator approval task commits exact live-probe approvals.

## Non-Goals / Scope Guard

- No live source calls by default.
- No package downloads, artifact downloads, source archive downloads, OCI layer pulls, package-manager invocation, installs, execution, scraping, crawling, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, or public truth creation.
- No rights-clearance, malware-safety, verified-installability, dependency-correctness, production-readiness, public launch, or deployment claims.

## Reviewer Instructions

Use evidence-only review. Confirm that blocked/default behavior is acceptable, that no unsafe product behavior was enabled, and that H2-BUNDLE-04 is the correct next local review-integration task. Return one of `PASS`, `PASS_WITH_NOTES`, `REQUEST_CHANGES`, or `BLOCKED`.
