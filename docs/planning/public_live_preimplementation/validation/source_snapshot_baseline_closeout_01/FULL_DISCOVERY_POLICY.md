# Full Discovery Policy

Full unittest discovery is not an AI-session command for this repo.

Relevant repo policy:

- `AGENTS.md` says full discovery must not run inside AI sessions by default.
- `docs/operations/FULL_DISCOVERY_CI_RUNBOOK.md` says operators should run the
  harness or GitHub Actions workflow and return compact artifacts.
- `docs/operations/TEST_AND_EVAL_LANES.md` reserves full discovery for
  promotion, nightly, manual local verification, and pre-main merge gates.

## Required External Artifacts

The operator or CI should return compact artifacts only:

- `full_unittest_summary.json`
- `failure_families.json`
- `failed_tests.txt`
- `git status --short --branch`

Raw stdout and stderr should not be pasted into AI chat.

## Current Decision

No current-head external summary exists. This closeout therefore stops at:

`WAITING_FOR_EXTERNAL_FULL_DISCOVERY`
