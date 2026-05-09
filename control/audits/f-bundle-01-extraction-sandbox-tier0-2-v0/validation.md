# Validation

F-BUNDLE-01 validation is offline and fixture-only. No private file access, execution, download, network call, source sync, evidence acceptance, candidate acceptance, public index mutation, or master index mutation occurred.

## Results

- `python scripts/validate_extraction_sandbox.py`: PASS
- `python scripts/run_fixture_extraction.py --target examples/extraction/targets/zip_manifest_target_v0.json --tiers 0,1,2 --check`: PASS
- `python scripts/summarize_extraction_results.py --input examples/extraction/results --check`: PASS
- `python -m unittest tests.extraction.test_extraction_sandbox`: PASS
- `python -m unittest tests.extraction.test_extraction_tiers`: PASS
- `python -m unittest tests.extraction.test_extraction_guards`: PASS
- `python -m unittest tests.operations.test_extraction_scripts`: PASS
- `python -m unittest discover -s tests -t .`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- Existing H1/H0/IA/core validators listed in the task prompt: PASS
- AIDE Lite doctor/validate/test/selftest/eval list/eval run/adapter validate: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, no errors. Warnings are from comparing the completed F-BUNDLE-01 diff against the F-BUNDLE-02 handoff packet and from pre-existing missing optional AIDE report refs.
- `py -3 .aide/scripts/aide_lite.py review-pack`: WARN, no errors; it wrote the latest review packet and reported the same verifier warning posture.

All validation remained offline. AIDE eval reported no provider/model calls and no network calls.
