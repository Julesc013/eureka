# Contract Gap Analysis

| Need | Current repo support | Gap classification | Notes |
| --- | --- | --- | --- |
| ResolutionRun | `contracts/resolution/run/resolution_run.v0.json`, `runtime/engine/interfaces/public/resolution_run.py` | can be handled inside fallback task | Existing engine record lacks fallback/candidate/source observation fields. Add backwards-compatible fields or notices. |
| WorkUnit | `runtime/search/need/workunit_plan.py`, `runtime/worker/workunit_queue/**`, `runtime/resolution_run/workunit_scheduler.py` | can be handled inside fallback task | Existing WorkUnits are disabled/local plans. Fallback can use a work-unit equivalent or policy-blocked WorkUnit record. |
| RunEvent | `contracts/resolution/run/run_event.v0.json`, `runtime/resolution_run/event_log.py` | can be handled inside fallback task | Engine run persistence does not store events. Use notices first or add event list if low risk. |
| SourceObservation | `contracts/source/action/source_observation_envelope.v0.json`, `contracts/runtime/source/observation.v0.json`, `runtime/source/action/**` | can be handled inside fallback task | Existing source-action envelopes are suitable if projected through the engine run. |
| EvidenceCandidate | `contracts/runtime/evidence_candidate.v0.json`, IA evidence/candidate code | can be handled inside fallback task | Candidate output must remain accepted=false and review_required=true. |
| SearchNeed | `contracts/query/search_need_record.v0.json`, `runtime/search/need/**` | can be handled inside fallback task | Public need runtime is not fully implemented; fallback can return public-safe need state without claiming durable public aggregation. |
| ReviewEvent | `contracts/stores/review_event.v0.json`, `runtime/review/queue/**` | should be deferred to review ledger | Fallback should not write review events; it can produce review handoff material only. |
| ReviewedRecord | `contracts/review/**`, `runtime/source/observation/internet_archive_reviewed_index.py`, `runtime/index/public/**` | should be deferred to review ledger | Fallback must not create reviewed records. |
| Public-safe view model | `runtime/gateway/public_api/public_search.py`, `runtime/public_search/ux_mvp.py`, snapshot projection code | should be deferred to SurfaceKernel unless minimal projection is needed | Public projection exists but not as a single SurfaceKernel. |
| Status vocabulary | `contracts/semantic/status.v0.json`, planning `PUBLIC_STATUS_VOCABULARY.md`, runtime statuses | blocking only if no mapping is possible | Contract shape has no enum. Runtime uses synonyms such as `needs_review`, `candidate_results_only`, `blocked_by_policy`, `unavailable`. |
| Action/affordance vocabulary | `contracts/semantic/affordance.v0.json`, `contracts/action/action_registry.v0.json`, public search action blocks | can be handled inside fallback task | Canonical action names need mapping to current public action IDs. |
| Policy gates | source action policy, IA live probe policy, public API forbidden params, candidate policy | can be handled inside fallback task | Add one fallback eligibility policy in engine run path and reuse existing source policies. |
| Visibility filters | public search, public alpha readonly, snapshot/UX projections | can be handled inside fallback task | Public-safe candidate/need projection must preserve redaction and action blocks. |
| Fallback disable switch | partial: public `source_policy`, source action policy, IA kill switch | can be handled inside fallback task | Add explicit fallback disabled behavior in engine run config/policy. |
| Source disable switch | partial: source family manifests, source policy, IA kill switch | can be handled inside fallback task | Add source allowlist and per-family disabled result. |
| Review freeze switch | partial review policies, no single global switch found | should be deferred to review ledger | Fallback should not write review state, so absence of a freeze switch is not blocking. |

## Blocking Before Fallback

No gap blocks fallback if the implementation keeps the first slice small and
does not require live contract rewrites.

Blocking would occur only if implementation insists on public view-model status
enums that cannot map to existing vocabulary. In that case run
`SEMANTIC-CORE-CONTRACTS-00` before fallback.

## Can Be Handled Inside Fallback Task

- Engine run fallback fields or notices.
- Fallback policy/disable/source allowlist.
- Candidate/need/unavailable/policy-blocked result mapping.
- Focused tests for no truth promotion and no public direct source call.

## Deferred To Review Ledger

- ReviewEvent contract alignment.
- ReviewedRecord promotion semantics.
- Review freeze switch.

## Deferred To SurfaceKernel

- Cross-surface canonical projection for public/API/text/snapshot parity.
- Full status/affordance rendering parity.
