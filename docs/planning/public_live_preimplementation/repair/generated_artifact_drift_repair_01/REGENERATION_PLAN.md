# Regeneration Plan

## Decision

Do not regenerate artifacts.

## Reason

The generated-artifact inventory is current and valid. The reported family was
caused by summary-parser drift, not by stale generated files.

## Chosen Repair Method

Fix the validator/reporting source of truth:

`tools/reporters/summarize_unittest_log.py`

The parser now treats `FAIL:` and `ERROR:` as unittest failure block headers only
when they are preceded by a unittest separator line.

## Artifacts Not Regenerated

- `site/dist/**`
- `site/dist/data/public_index/**`
- `snapshots/**`
- generated checksums
- public/master/reviewed indexes

## External Rerun

A future external full-discovery rerun must regenerate the external summary
artifacts outside the repo.

