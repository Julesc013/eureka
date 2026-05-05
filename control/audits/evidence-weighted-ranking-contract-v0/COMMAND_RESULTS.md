# Command Results

Recorded during P84 local verification on 2026-05-05. Commands were run from the repo root and did not call external source APIs, enable connectors, deploy, mutate indexes, or apply ranking to live search.

## P84 Focused Checks

- `python scripts/validate_evidence_weighted_ranking_assessment.py --all-examples`: passed, 5 examples.
- `python scripts/validate_evidence_weighted_ranking_assessment.py --all-examples --json`: passed, JSON parsed.
- `python scripts/validate_ranking_explanation.py --all-examples`: passed, 5 examples.
- `python scripts/validate_ranking_explanation.py --all-examples --json`: passed, JSON parsed.
- `python scripts/validate_evidence_weighted_ranking_contract.py`: passed.
- `python scripts/validate_evidence_weighted_ranking_contract.py --json`: passed, JSON parsed.
- `python scripts/dry_run_evidence_weighted_ranking.py --left-title "Strong evidence result" --right-title "Weak evidence result" --json`: passed, stdout-only dry run.
- P84 focused unittest set: passed, 16 tests.

## Prerequisite Contract Checks

- P79 object page, P80 source page, P81 comparison page, P82 identity resolution, and P83 result merge/deduplication validators: passed.
- Connector approval pack validators for Internet Archive metadata, Wayback/CDX/Memento, GitHub Releases, PyPI, npm, and Software Heritage: passed.
- Source sync worker, source cache/evidence ledger, candidate index, candidate promotion, known absence, and query-intelligence validators: passed.

## Search, Site, Eval, And Safety Checks

- External baseline comparison batch 0: valid but not eligible for comparison because 0 manual observations are recorded; 39 batch slots remain pending.
- Hosted deployment evidence: valid with warnings; hosted backend is not configured and static verification remains operator-gated/failed.
- Hosted public search rehearsal and public search safety evidence: passed using local bounded rehearsal paths.
- Public search contract, result card contract, safety, local runtime, smoke, public index builder/check, static site build/check/validate, publication inventory, static artifact, generated artifact drift, public alpha smoke: passed.
- Archive resolution evals: passed, 6/6 tasks satisfied.
- Search usefulness audit: completed; local statuses were 5 covered, 40 partial, 10 source gaps, 7 capability gaps, and 2 unknown; external baselines remain pending manual observation.
- Python oracle golden check: passed.

## Broad Test Lanes

- `python -m unittest discover -s tests/scripts -t .`: passed, 569 tests.
- `python -m unittest discover -s tests/operations -t .`: passed, 550 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed, 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed, 25 tests.
- `python -m unittest discover -s runtime -t .`: passed, 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed, 168 tests.
- `python -m unittest discover -s tests -t .`: passed, 1288 tests.
- `python scripts/check_architecture_boundaries.py`: passed, no architecture-boundary violations.
- `git diff --check`: passed with line-ending warnings for existing generated static artifacts.

## Optional

- `cargo --version`: unavailable; `cargo` is not on PATH, so optional Rust checks were not run.
