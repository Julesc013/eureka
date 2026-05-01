# Command Results

P63 local verification was run on 2026-05-02 from the repository worktree.

## P63 Required Commands

- `python scripts/validate_probe_queue_item.py --all-examples`
  - passed; 3 examples valid
- `python scripts/validate_probe_queue_item.py --all-examples --json`
  - passed; JSON parsed and reported 3 valid examples
- `python scripts/validate_probe_queue_contract.py`
  - passed; report `probe_queue_v0` valid
- `python scripts/validate_probe_queue_contract.py --json`
  - passed; JSON parsed with contract-only warning
- `python scripts/dry_run_probe_queue_item.py --label "Check IA metadata for Windows 7 app query" --kind source_metadata_probe --json`
  - passed; stdout-only dry-run item emitted

## Query Intelligence Regression

- P59 query observation example and contract validators passed.
- P60 shared query/result cache example and contract validators passed.
- P61 search miss ledger example and contract validators passed.
- P62 search need record example and contract validators passed.

## Public Search And Static Regression

- P58 hosted public search rehearsal passed: 60/60 checks, 9 safe routes, 5 safe
  queries, 34/34 blocked requests, 584 public-index documents.
- P57 public search safety evidence passed: 64/64 checks, 32/32 blocked
  requests.
- Static site search integration, public search index builder, public search
  index, hosted wrapper, public search contracts, public search safety, local
  public search runtime, static site build/validation, publication inventory,
  public static site, GitHub Pages static artifact check, generated artifact
  drift, and public alpha smoke all passed.

## Eval Status

- `python scripts/run_archive_resolution_evals.py` passed with 6/6 tasks
  satisfied locally.
- `python scripts/run_search_usefulness_audit.py` and `--json` passed over 64
  queries; current status remains mixed/partial by design.
- `python scripts/report_external_baseline_status.py --json` passed with 0
  observed external baselines and 192 pending manual observation slots.

## Unit And Boundary Checks

- `python -m unittest discover -s tests/scripts -t .` passed: 320 tests.
- `python -m unittest discover -s tests/operations -t .` passed: 467 tests.
- `python -m unittest discover -s tests/hardening -t .` passed: 53 tests.
- `python -m unittest discover -s tests/parity -t .` passed: 25 tests.
- `python -m unittest discover -s runtime -t .` passed: 320 tests.
- `python -m unittest discover -s surfaces -t .` passed: 168 tests.
- `python -m unittest discover -s tests -t .` passed: 956 tests.
- `python scripts/check_architecture_boundaries.py` passed.
- `git diff --check` passed with CRLF conversion warnings only.

## Optional Commands

- `cargo --version` was unavailable in this environment, so optional Cargo
  checks were not run.
