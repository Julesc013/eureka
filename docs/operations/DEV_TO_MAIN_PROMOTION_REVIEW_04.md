# DEV TO MAIN PROMOTION REVIEW 04

This runbook covers promotion of the public alpha read-only baseline from
`dev` to `main`.

Promotion is allowed only when:

- `origin/main` is an ancestor of `origin/dev`.
- `origin/main` is not ahead of `origin/dev`.
- The working tree is clean before branch mutation.
- External full discovery has passed for the current dev head or only
  promotion evidence/validator/audit files were added afterward.
- Public alpha read-only, hosting, closeout, snapshot relay, source wave,
  source action, and prior source snapshot promotion evidence are present.
- No deployment, production readiness, public launch readiness, live source
  call, public mutation, public live source fanout, download, extraction,
  model/provider call, or private local state commit is required.

Full unittest discovery must not be rerun inside AI sessions for this task.
