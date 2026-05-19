# DEV And IA Promotion Blocker Repair

`DEV-AND-IA-PROMOTION-BLOCKER-01` repairs the full-discovery failures that blocked promotion of the current dev baseline.

Promotion is still not performed by this repair task.

Repaired blocker lanes:
- candidate-index record ownership and examples
- contract taxonomy inventory for `contracts/repo`
- runtime/source-observation leakage vocabulary
- HUNT/LOCAL promotion-state validation

Boundaries preserved:
- no main promotion or main push
- no new live IA probe
- no downloads, uploads, extraction, model/provider calls, or deployment
- no operator instance, committed `data/public_index`, master index, or public fanout mutation
- no production readiness, public launch readiness, full Archive.org integration, or marketplace/app-store readiness claim

Next task:

```text
DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW - Promote dev IA pilot plus repo layout canon baseline to main
```
