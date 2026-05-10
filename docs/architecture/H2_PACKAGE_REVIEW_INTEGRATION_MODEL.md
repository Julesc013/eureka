# H2 Package Review Integration Model

H2 review integration is a rehearsal layer between fixture/live-probe outputs and future source-family expansion.

## Boundaries

- No new live source calls by default.
- No package, artifact, source archive, OCI layer, signature, SBOM, or vulnerability payload downloads.
- No package-manager invocation, install, or execution.
- No source cache, evidence ledger, review queue, public index, or master index mutation.
- No source, evidence, candidate, package identity, dependency correctness, or public truth acceptance.

## Validation

- `python scripts/validate_h2_package_review_quality_audit.py`
- `python scripts/integrate_h2_package_review.py --input-dir examples/connectors/h2_package_registries/replay_results --check`
- `python scripts/summarize_h2_package_quality_delta.py --input-dir examples/connectors/h2_package_registries/review_integration --check`
- `python scripts/audit_h2_package_registry_wave.py --check`
