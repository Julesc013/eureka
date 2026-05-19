# Promotion Decision

Decision: promote `dev` to `main` by fast-forward only if the final pre-push
branch check still shows `origin/main` as an ancestor of `dev`.

Scope:

- IA metadata pilot through closeout.
- Repo layout canon through `REPO-LAYOUT-CANON-01`.
- `DEV-AND-IA-PROMOTION-BLOCKER-01` full-discovery blocker repair.

No force push, rebase, history rewrite, branch deletion, deployment, production
readiness claim, public launch readiness claim, full Archive.org integration
claim, marketplace/app-store readiness claim, download, upload, extraction, or
model/provider call is permitted.

Promotion gate:

- `python -m unittest discover -s tests -t .` passed after blocker repair.
- IA validators pass.
- repo layout canon validates.
- runtime leakage validators pass.
- architecture and generated artifact gates pass.
- AIDE gates pass.
