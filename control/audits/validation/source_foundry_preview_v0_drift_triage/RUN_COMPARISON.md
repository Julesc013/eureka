# Source Foundry Preview v0 Run Comparison

Generated: `2026-06-19T02:48:51Z`

## Result

- counts match: true
- failed-tests hash match: true
- failure-family hash match: false
- deterministic assessment: materially similar and likely deterministic on failed-test identity because counts and failed_tests hash match across red ingests

## Run 1

- head: `670a573276d220d8136942de38eed4e0115749a5`
- tests/failures/errors: 5792 / 43 / 7
- failed-tests hash: `sha256:38638a1be321b938be5cb51ed0c743cb8b740e200f366017074b68e92277e8d6`
- artifact detail: committed compact ingest only; raw first-run artifacts were overwritten by reusing the same run id

## Run 2

- head: `f16d828714614c5ac7f84ab3e85aebc06cbf7a5d`
- tests/failures/errors: 5792 / 43 / 7
- failed-tests hash: `sha256:38638a1be321b938be5cb51ed0c743cb8b740e200f366017074b68e92277e8d6`
- artifact detail: current external artifact set available under ../eureka-test-runs/source_foundry_preview_v0_checkpoint_00

## Missing Artifacts

- first run raw full_unittest_summary.json
- first run raw failure_families.json
- first run raw stdout/stderr logs
