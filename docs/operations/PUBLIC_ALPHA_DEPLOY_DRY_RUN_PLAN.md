# Public Alpha Deploy Dry-Run Plan

`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` is the next task after a passing launch
candidate. It should rehearse packaging, environment, smoke checks, security
headers, observability, and rollback without public launch semantics unless a
future task explicitly authorizes them.

The dry run should prefer:

- static snapshot site
- read-only relay service

It must continue to forbid:

- public mutation
- public live source fanout
- downloads or uploads
- extraction
- model/provider calls
- production or public launch claims

Manual approval is required before any deployment or launch action.
