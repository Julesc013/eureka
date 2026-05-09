# Extraction Sandbox Contract

`contracts/extraction/extraction_sandbox.v0.json` defines the F-BUNDLE-01 fixture sandbox boundary. The sandbox accepts only repo-local synthetic fixtures or explicit temp-test fixtures, allows ZIP and TAR containers, and records resource, path, archive-bomb, execution, network, and recursion policy.

The sandbox is not a downloader, live source connector, malware scanner, installer runner, recursive extraction engine, source-cache writer, evidence ledger writer, review decision maker, public index writer, or master index writer.

Validation:

- `python scripts/validate_extraction_sandbox.py`
- `python scripts/run_fixture_extraction.py --target examples/extraction/targets/zip_manifest_target_v0.json --tiers 0,1,2 --check`
