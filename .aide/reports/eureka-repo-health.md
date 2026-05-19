# Eureka Repo Health

Updated: 2026-05-19

Current recommended task: DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW - Promote dev IA
pilot plus repo layout canon baseline to main.

Last completed task: DEV-AND-IA-PROMOTION-BLOCKER-01 - Resolve blocking
full-discovery failures before main promotion.

Status: promotion blockers repaired; main promotion not performed in the repair
task. The preferred local instance path remains `../instances/default`, with
legacy sibling `../eureka-instance` explicit-only.

The Internet Archive metadata pilot is closed as a metadata-only local-source
vertical slice. IA-00 through IA-07 validate through reviewed local index
rebuild, search result proof, object packet proof, and absence packet proof.

The pilot proves reusable source-family patterns: policy gates, fixture replay,
bounded metadata probes, TLS diagnostics, redaction, source cache, evidence
candidates, provisional candidates, review queue, promotion dry-run, reviewed
local index rebuild, temp-instance proofs, non-claims, and boundary reports.

All write-capable stages remain `temp_explicit_instance_only`. The operator
instance was not mutated. No raw response body, committed `data/public_index`
mutation, master index mutation, hosted public search mutation, extraction,
model/provider call, download, upload, deployment, production readiness claim,
or public launch readiness claim occurred.

DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW checked current `dev`, including the IA
metadata pilot and REPO-LAYOUT-CANON-01. The follow-up blocker repair resolved
candidate-index, contract taxonomy, runtime/source-observation leakage, and
HUNT/LOCAL promotion-state failures. `main` was not promoted by the repair task.

The next task is to rerun the dev/IA promotion review. Workbench Foundation
remains the next product-shaping task after `main` is safely fast-forwarded.
