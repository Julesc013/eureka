# Full Discovery Evidence

The external harness result used for this promotion is the compact summary at:

`../eureka-test-runs/source_snapshot_closeout/full_unittest_summary.json`

Committed promotion evidence records:

- status: PASS
- tests_run: 5008
- failures: 0
- errors: 0
- exit_code: 0
- git working tree clean: true

The compact summary contains an expected refusal-path trace:

`refusing forbidden output root: site/dist`

Because unittest returned OK with exit code 0 and zero failures/errors, this is
classified as `expected_refusal_trace_nonblocking`.

