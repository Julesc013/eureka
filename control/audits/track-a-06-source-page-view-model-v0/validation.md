# TRACK-A-06 Validation

Observed validation for the SourcePage view model contract bundle.

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short` | PASS | Expected A06 files before commit. |
| `git diff --check` | PASS | Exit 0; local Git emitted LF-to-CRLF notice only. |
| `python -m json.tool control/inventory/publication/source_page_view_model_policy.json` | PASS | JSON parses. |
| `python -m json.tool control/audits/track-a-06-source-page-view-model-v0/track_a_06_report.json` | PASS | JSON parses. |
| `python scripts/validate_representation_contracts.py` | PASS | Existing A01 representation bundle still validates. |
| `python scripts/validate_semantic_renderer_parity.py` | PASS | Existing A02 semantic parity bundle still validates. |
| `python scripts/validate_route_view_representation_matrix.py` | PASS | Existing A03 matrix bundle still validates. |
| `python scripts/validate_search_page_view_model.py` | PASS | Existing A04 SearchPageView bundle still validates. |
| `python scripts/validate_object_page_view_model.py` | PASS | Existing A05 ObjectPageView bundle still validates. |
| `python scripts/validate_source_page_view_model.py` | PASS | A06 schema, policy, and examples validate. |
| `python -m unittest discover -s tests -t .` | PASS | 1631 tests passed. |
| `python scripts/check_architecture_boundaries.py` | PASS | 479 Python files checked; no violations. |
| `git check-ignore .aide.local/` | PASS | `.aide.local/` is ignored. |
| Strict secret scan over changed paths | PASS | No provider keys, private-key blocks, API-key assignments, or auth-token assignments found. |
| ASCII scan over changed paths | PASS | Changed files are ASCII-only. |
| Generated site artifact status | PASS | No `site/` artifacts changed. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Optional/future AIDE artifacts remain warnings only. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Review packet optional refs remain WARN-only. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Internal AIDE checks pass. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Internal AIDE selftest passes. |
| `py -3 .aide/scripts/aide_lite.py verify` | WARN | WARN-only, 0 errors; stale active compact task packet still names TRACK-A-01 and review packet optional refs are missing. |
| `py -3 .aide/scripts/aide_lite.py eval list` | PASS | 14 active deterministic golden tasks listed. |
| `py -3 .aide/scripts/aide_lite.py eval run` | PASS | 14/14 golden tasks passed. |
| `py -3 .aide/scripts/aide_lite.py review-pack` | WARN | Wrote review packet; verifier result WARN with 0 errors. |
| `py -3 .aide/scripts/aide_lite.py adapter validate` | PASS | Adapter surface is current. |

## Notes

- The repo-local compact task packet still names TRACK-A-01. The active scope
  for this audit is the explicit TRACK-A-06 user task and this audit pack.
- WARN-only AIDE verifier output is acceptable only with zero errors.
