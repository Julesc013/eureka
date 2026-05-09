# Validation

Final validation for H0-BUNDLE-01:

```text
git diff --check
```

Result: PASS with Git line-ending notices only.

```text
python -m json.tool <H0 contract, inventory, and report JSON files>
```

Result: PASS for 19 files.

```text
python scripts/validate_source_os_foundation.py
python scripts/summarize_source_registry_v2.py --input examples/sources/source_registry_v2/minimal_source_registry_v2.json --check
python -m unittest tests.contracts.test_source_os_foundation_contracts
python -m unittest tests.operations.test_source_os_foundation_scripts
```

Result: PASS. Focused tests ran 19 tests.

```text
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

Result: PASS. Full unittest discovery ran 2603 tests. Architecture boundary
check found no violations.

```text
python scripts/validate_ia_readiness_polish.py
python scripts/validate_ia_metadata_connector_foundation.py
python scripts/validate_ia_metadata_live_probe.py
python scripts/validate_ia_review_integration.py
python scripts/validate_local_source_cache_runtime.py
python scripts/validate_local_evidence_ledger_runtime.py
python scripts/validate_source_cache_to_evidence_bridge.py
python scripts/validate_local_review_queue_runtime.py
python scripts/validate_candidate_promotion_dry_run.py
python scripts/validate_pack_builder_runtime.py
python scripts/validate_pack_export_runtime.py
```

Result: PASS.

```text
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
py -3 .aide/scripts/aide_lite.py test
py -3 .aide/scripts/aide_lite.py selftest
py -3 .aide/scripts/aide_lite.py verify
py -3 .aide/scripts/aide_lite.py eval list
py -3 .aide/scripts/aide_lite.py eval run
py -3 .aide/scripts/aide_lite.py review-pack
py -3 .aide/scripts/aide_lite.py adapter validate
```

Result: PASS except `verify`, which is WARN with zero errors. The WARN entries
are future H0-BUNDLE-02 handoff paths that do not exist yet and existing
optional AIDE status references.

No live source calls, API calls, provider calls, downloads, scraping, source
sync, public-index mutation, master-index mutation, evidence acceptance,
candidate acceptance, source truth acceptance, or product behavior changes were
performed.
