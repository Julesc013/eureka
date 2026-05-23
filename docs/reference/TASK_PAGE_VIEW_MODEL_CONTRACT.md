# TaskPage View Model Contract

TaskPageView v0 defines the public meaning layer for future work units,
node-task handoff pages, and bounded task summaries. It is contract and
governance work only. It does not enable nodes, autonomous execution, live
source access, model/provider calls, downloads, uploads, public submissions,
or master-index mutation.

## Purpose

A task is a bounded request for governed work, not autonomous permission.
TaskPageView makes task identity, type, status, scope, inputs, allowed actions,
forbidden actions, expected outputs, future capability requirements, execution
posture, evidence posture, rights/risk/privacy posture, blocked actions, and
limitations explicit before runtime work exists.

## Required Meaning

TaskPageView preserves:

- canonical task identity and route
- task type, status, scope, and input references
- allowed and forbidden actions
- output contract and expected output posture
- related need, candidate, source, pack, and review references
- future node policy and capability requirements as unavailable/deferred
  posture
- execution-disabled status
- evidence posture and truth boundaries
- rights, risk, and privacy posture
- limitations, warnings, and unresolved gaps

## Current Boundary

Current examples must not imply:

- active node runtime
- autonomous execution
- live source access, live probes, scraping, crawling, or arbitrary URL fetches
- model or provider calls
- downloads, installers, execution, uploads, accounts, telemetry, or public
  submission runtime
- source sync
- master-index mutation or public truth mutation
- rights clearance, malware safety, verified installability, safe execution,
  authorized bulk access, or production suitability

## Related Contracts

- `contracts/view/pages/task_page.v0.json`
- `control/inventory/publication/task_page_view_model_policy.json`
- `docs/reference/NEED_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/CANDIDATE_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/SOURCE_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No node runtime, autonomous runtime, model/provider calls, or live source
  access.
- No source sync, downloads, uploads, accounts, telemetry, or public
  submissions.
- No master-index mutation.
- No public truth from task inputs, source observations, evidence candidates,
  contribution items, AI drafts, or work-unit outputs.
