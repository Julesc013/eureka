# F0 Start Branch Policy

Current decision: `resume_f0`.

Recommended start branch while promotion remains plan-only: `dev`.

Reason: the recovered R0 runtime baseline is on `dev`, and `main` remains intentionally behind until an explicit dev-to-main promotion apply action is run.

## If Promotion Is Applied First

If `DEV-TO-MAIN-MERGE-R0` is explicitly applied and pushed, F0 may start from `main` after the final promotion validation lane passes again.

## If Promotion Is Delayed

If the operator keeps promotion plan-only, F0 may resume from `dev` with this documented branch policy. This avoids starting F0 from stale `main` while also preserving the rule that no branch mutation happens without explicit apply authorization.

## F0 Requirements

- F0 must use the recovered R0 runtime seams: source observation, source cache, evidence ledger, review queue, reviewed public index, and the one-source PyPI metadata pipeline evidence.
- F0 must not reintroduce scaffold-only completion.
- F0 must not treat promotion as deployment or public launch.
- F0 must keep source calls, connector expansion, package downloads, source sync, and site regeneration disabled unless a future reviewed queue item explicitly permits them.
