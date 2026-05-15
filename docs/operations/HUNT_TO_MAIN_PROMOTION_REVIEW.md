# HUNT To Main Promotion Review

HUNT-12 does not merge to main.

The promotion review task must:

- compare `origin/main` and `origin/dev`
- confirm HUNT closeout result remains pass
- re-run generated artifact cleanliness after commit
- re-check runtime leakage gates
- confirm no deployment, production readiness claim, or public launch readiness
  claim
- produce an explicit merge plan if promotion is still desired

Branch mutation is forbidden by default in the review-prep script.
