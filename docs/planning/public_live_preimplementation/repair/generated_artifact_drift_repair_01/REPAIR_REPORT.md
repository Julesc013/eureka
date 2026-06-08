# Repair Report

## Task

`GENERATED-ARTIFACT-DRIFT-REPAIR-01`

## Status

`PASS_WITH_WARNINGS`

## Summary

The external ingest reported one generated-artifact family:
`unittest-cb1ded72f5fc441c`.

The reported label was:

`refusing forbidden output root: site/dist`

That string is not a unittest label. It is expected negative-path output emitted
by source-family and generated-artifact safety tests when they verify that
scripts refuse unsafe output roots such as `site/dist`.

Current repo generated-artifact checks are green. Resummarizing the old external
stdout/stderr with the repaired parser removes the bogus family:

- `contains_forbidden_output_root`: `false`
- `generated_family_count`: `0`

## Repair

`tools/reporters/summarize_unittest_log.py` now recognizes `FAIL:` and `ERROR:`
as unittest failure headers only when preceded by a unittest separator line. A
regression test covers plain validator output containing
`ERROR: refusing forbidden output root`.

## Gates

Public alpha remains blocked.

`dev -> main` promotion remains blocked.

The source/snapshot release gate remains blocked pending remaining family repair
and external full-discovery rerun.

