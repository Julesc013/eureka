# Promotion Decision

Decision: blocked. Do not promote `dev` to `main` while full unittest discovery
has blocking failures.

Scope:

- IA metadata pilot through closeout.
- Repo layout canon through `REPO-LAYOUT-CANON-01`.

No force push, rebase, history rewrite, branch deletion, deployment, or public
readiness claim is permitted.

Blocking reason:

- `python -m unittest discover -s tests -t .` failed with `17` failures and `5`
  errors, including candidate-index, source-observation/runtime leakage,
  HUNT/LOCAL promotion-state, and contract taxonomy lanes.
