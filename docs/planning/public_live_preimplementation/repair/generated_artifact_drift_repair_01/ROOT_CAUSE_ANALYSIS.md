# Root Cause Analysis

## Root Cause

The full-discovery summary parser in
`tools/reporters/summarize_unittest_log.py` matched any line beginning with
`ERROR:` or `FAIL:` as a unittest failure header.

That was too broad. Several tests intentionally execute scripts with forbidden
output roots and assert that they fail safely. Those scripts print diagnostic
lines such as:

`ERROR: refusing forbidden output root: site/dist`

The negative-path tests pass, but the compact summary parser misclassified the
diagnostic line as a failed unittest label.

## Why This Is Not Generated Output Drift

Current generated-artifact validators and check-mode generators report no drift.
The stale artifact was the external compact summary itself, not `site/dist`,
snapshots, checksums, public indexes, or generator outputs.

## Repair Type

`validator_expectation_drift`

More specifically: full-discovery summary parser false positive.

