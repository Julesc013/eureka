# DEV TO MAIN PROMOTION REVIEW 03

This runbook covers the source snapshot baseline promotion from `dev` to
`main`.

Promotion is allowed only when:

- `origin/main` is an ancestor of `origin/dev`.
- `origin/main` is not ahead of `origin/dev`.
- The working tree is clean before branch mutation.
- External full discovery has passed through the compact harness summary.
- SourceActionKernel, SourceWave, SnapshotRelay, and source snapshot closeout
  evidence are present.
- No production readiness, public launch readiness, deployment, live source
  call, download, extraction, model/provider call, or private local state commit
  is required.

Full unittest discovery must not be rerun inside AI sessions for this task.

