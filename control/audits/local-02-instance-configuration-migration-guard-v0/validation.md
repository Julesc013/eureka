# Validation

LOCAL-02 validation was run from `LOCAL-02-instance-migration-guard`.

PASS:

- `git diff --check`
- JSON syntax checks for LOCAL-02 policies, inventories, and audit report
- `python scripts/validate_local_instance_migration_guard.py --json`
- `python -m unittest tests.operations.test_local_instance_migration_guard`
- `python -m unittest tests.operations.test_local_instance_schema_version`
- `python -m unittest tests.operations.test_local_instance_bootstrap`
- `python -m unittest tests.operations.test_local_instance_policy`
- `python scripts/validate_local_instance_bootstrap.py`
- manual ignored-instance smoke:
  - `python scripts/eureka_init_instance.py --instance ./eureka-instance --json`
  - `python scripts/eureka_validate_instance.py --instance ./eureka-instance --json`
  - `python scripts/eureka_instance_status.py --instance ./eureka-instance --json`
  - `python scripts/eureka_instance_migration_status.py --instance ./eureka-instance --json`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json` after commit
- `python scripts/validate_ia_readiness_polish.py --json` after adding the LOCAL route compatibility note to the task packet
- AIDE Lite `doctor`, `validate`, `test`, and `selftest`

WARN:

- `python scripts/validate_local_appliance_track.py` passed with the expected warning that `origin/dev` is ahead of `origin/main` after Local Appliance queue work.
- AIDE Lite `verify` and `review-pack` returned warnings from stale AIDE diff-scope metadata for the LOCAL-02 allowed paths.
- `python scripts/check_generated_artifact_cleanliness.py --check --json` failed before commit because the new LOCAL-02 audit generated directory was uncommitted. It passed after commit once those audit generated samples were tracked.
- `python scripts/check_generated_artifact_drift.py --json`, `python scripts/build_public_search_index.py --check`, `python scripts/validate_public_search_index.py`, and `python scripts/validate_public_search_index_builder.py` fail on pre-existing public search index generated artifact drift: `site/dist/data/public_index/search_documents.ndjson` and `site/dist/data/public_index/checksums.sha256`.

KNOWN PRE-EXISTING FAILURE:

- `python scripts/audit_runtime_architecture_leakage.py --check --json`
- `python scripts/validate_runtime_architecture_leakage.py`
- `python -m unittest discover -s tests -t .`

The runtime leakage gate remains at the known baseline: 1030 new unallowlisted production findings, 285 blockers, and 2477 allowlisted findings. Final full unittest discovery ran 4108 tests and failed with 2 failures and 5 errors from the known runtime leakage gate plus public search index generated artifact drift; LOCAL-02 did not modify runtime, contracts, surfaces, site, native, crates, examples, or `eureka-instance/**`.
