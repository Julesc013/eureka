# Review Boundary Audit

## Findings

Review boundary doctrine is broadly represented in current repo code.

## Candidate Cannot Self-Promote

Evidence:

- `runtime/candidate_store/runtime.py` sets candidate outputs as not reviewed
  truth and blocks public mutation.
- Candidate states include review-oriented states such as `needs_review`,
  `review_item_created`, and rejection states.
- Candidate boundary reports keep `accepted_truth_created=false` and
  `reviewed_index_mutated=false`.

Gap:

- Some runtime state names need mapping to canonical public `candidate`.

## Source Observation Cannot Write Reviewed Truth

Evidence:

- `runtime/source/action/action_kernel.py` sets source action output as plans,
  observations, and candidate/review handoff material, not truth.
- `source_observation_envelope.v0` requires `accepted_truth=false`.
- IA observation/cache/evidence flows validate `accepted_truth=false` and no
  reviewed/master index mutation.

Gap:

- Fallback must avoid persistent source-cache/index writes unless explicitly
  governed by a later task.

## AI Output Cannot Promote

Evidence:

- AI escalation/provider modules are disabled by default.
- Public and review policies repeatedly block model/provider use and accepted
  truth.

Fallback requirement:

- No model/provider output is part of this fallback.

## Synthetic Fixtures Cannot Promote

Evidence:

- Fixture source action adapter marks fixture behavior as not truth.
- Source-action and candidate tests check non-claim boundaries.

Fallback requirement:

- Fixture/mock fallback tests must assert no reviewed truth or public index
  mutation.

## Review Event Required For Reviewed Record

Evidence:

- `runtime/review/queue/**` records review decisions and events.
- `runtime/local/review/**` separates decisions from reviewed-index rebuilds.
- IA reviewed index code reconstructs reviewed local records from promotion
  preview and review decision data.

Gap:

- The exact public-live review ledger contract needs later alignment in
  `REVIEW-LEDGER-00`.

## Rejection And Supersession Explainability

Evidence:

- Review queue decisions include reject, block, supersede, request more
  evidence, and reason validation.
- `contracts/stores/review_event.v0.json` includes `blocked` and `superseded`.

Gap:

- Public projection of rejected/superseded fallback candidates should be
  deferred until review ledger and SurfaceKernel alignment.

## Preflight Conclusion

Fallback may create candidate/need/policy-blocked/unavailable states, but must
not create review decisions, reviewed records, accepted truth, or reviewed/public
index mutations.
