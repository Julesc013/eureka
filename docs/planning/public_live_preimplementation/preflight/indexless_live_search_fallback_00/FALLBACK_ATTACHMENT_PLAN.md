# Fallback Attachment Plan

## Entry Point

Attach fallback inside `runtime/engine/resolution_runs/service.py`, specifically
behind deterministic/planned search run execution in `_run_search`.

Do not attach fallback as authoritative behavior in:

- `runtime/gateway/public_api/public_search.py`
- `surfaces/**`
- `site/**`
- direct source adapter routes

## Future Flow

```text
DeterministicSearchRunRequest or PlannedSearchRunRequest
-> LocalResolutionRunService._run_search
-> SearchService.search(SearchRequest)
-> if local results are sufficient, return unchanged run
-> if local results are unavailable or insufficient, evaluate fallback policy
-> if disabled or source disallowed, record policy_blocked/unavailable state
-> if allowed, create bounded source work unit or source action request plan
-> call allowlisted source metadata adapter through runtime/source seam
-> create SourceObservation/envelope or equivalent
-> map observation to EvidenceCandidate/CandidateRecord or SearchNeed
-> attach candidate/need/degraded lane to ResolutionRunRecord or notices
-> gateway/public surfaces project public-safe candidate/need state
```

## Local Lookup Check

Use existing `self.search_service.search(SearchRequest.from_parts(search_query))`
inside `_run_search`.

Sufficient local result:

- `response.results` is non-empty.
- The existing reviewed/local result path remains unchanged.

Fallback-eligible local miss:

- `response.results` is empty.
- Absence report indicates local bounded miss.
- Policy allows fallback.

Optional insufficient-result condition:

- Use a conservative flag or threshold only if repo already supports it.
- Do not classify weak reviewed/local results as false without tests.

## Fallback Eligibility Check

Required inputs:

- fallback enabled flag
- source family allowlist
- per-source/source-family disabled state
- budget: max requests, max candidates, timeout
- projection context: public vs operator
- no public fanout flag

## Policy Gate

Policy must enforce:

- no arbitrary URL input
- no credentials
- no downloads/uploads/extraction/execution
- no raw response commit
- no reviewed/public/master index mutation
- no accepted truth
- review_required=true for candidates

Reuse existing gates where possible:

- `runtime/source/action/action_kernel.py`
- `runtime/source/observation/policy.py`
- `runtime/source/observation/internet_archive_live_probe.py`
- public API forbidden-parameter checks

## Source Allowlist Check

First implementation should allow only the selected metadata-only source
family, likely Internet Archive metadata if approved by policy.

Any non-allowlisted family returns `policy_blocked` or `unavailable` with a
notice, not a source call.

## Budget Check

Use hard caps:

- max HTTP requests
- max rows/candidates
- timeout seconds
- retry attempts

Budget exceeded returns a degraded state and no verified result.

## WorkUnit Creation Or Equivalent

Preferred first slice:

- create a run-local source work-unit equivalent or source action request plan
  rather than enqueueing executable WorkUnits.
- if using `runtime/search/need/workunits.py`, source-probe WorkUnits must remain
  blocked by policy.

## Source Adapter Call Or Equivalent

Use an adapter/provider through the engine service, not the public search
surface.

Candidate implementation options:

- wrap `runtime/source/observation/archive_org_public_metadata.py`
- use `runtime/source/action/action_kernel.py` plus a source adapter
- use source-wave adapter code where fixture/metadata behavior fits

## SourceObservation Creation Or Equivalent

Store or return:

- source family
- source action/request ID
- observation IDs or observation envelope
- live/external call flags
- raw response commit false
- review_required true
- accepted_truth false
- limitations/warnings

## Candidate/SearchNeed Creation Or Equivalent

Candidate:

- use `runtime/candidate_store/runtime.py` normalization or equivalent.
- candidate state maps to public `candidate`.
- no reviewed record ref.

SearchNeed:

- use `runtime/search/need/**` only when local/public policy permits.
- otherwise return a public-safe need state in the run output without claiming
  durable public need creation.

## Public-Safe Projection

Public output must:

- show reviewed/local results unchanged.
- label fallback candidates as candidate/review-required.
- show need/policy-blocked/unavailable states honestly.
- block operator actions: review, promote, reject, rebuild_index.
- never call source providers directly from UI or public route code.

## Logging And Events

Minimum:

- run notices record fallback eligibility, policy, source family, budget result,
  and degraded outcome.

Preferred if low risk:

- add event list compatible with existing `run_event.v0` concepts.

## Disable Switch Behavior

- fallback disabled: no source call, result state `policy_blocked`,
  `unavailable`, or `need` with an explanatory notice.
- source family disabled: no source call, result state `policy_blocked` or
  `unavailable`.
- timeout/budget: no retry loop beyond policy; degraded state only.

## Failure And Degradation Behavior

Failures map to:

- `policy_blocked`
- `unknown`/`unavailable`
- `need`

They never map to `verified`.
