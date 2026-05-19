# Eureka Repo Health

Updated: 2026-05-19

Current recommended task: DEV-AND-IA-PROMOTION-BLOCKER-01 - Resolve blocking
full-discovery failures before main promotion.

Last completed task: IA-PILOT-CLOSEOUT-01 - Internet Archive Metadata Pilot
Closeout.

Status: blocked for main promotion. The preferred local instance path remains
`../instances/default`, with legacy sibling `../eureka-instance`
explicit-only.

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
metadata pilot and REPO-LAYOUT-CANON-01. Focused IA/layout/AIDE gates passed,
but full unittest discovery failed with `17` failures and `5` errors in
candidate-index, contract taxonomy, runtime/source-observation leakage, and
HUNT/LOCAL promotion-state lanes. `main` was not promoted.

Workbench Foundation remains the next product-shaping task after the promotion
blockers are resolved and `main` is safely fast-forwarded.
