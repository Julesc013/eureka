# AIDE Latest Task Packet

## PHASE

SOURCE_WAVE_REVIEW_GATE - REVIEW-IA-CANDIDATES-BATCH-00

## GOAL

Prepare deterministic review-batch material from the IA source-observation,
candidate-index, and evidence-summary deltas. Record review-ledger decisions
only when an explicit operator decision input file is supplied.

This is not automatic review, automatic promotion, reviewed-record
materialization, reviewed/master-index refresh, public-index mutation, snapshot
publication, public exposure, public launch, source/provider expansion, or a
network/provider task.

## WHY

The automated source/evidence preparation pipeline has reached the human review
boundary:

```text
56 source observations
-> 56 provisional candidates
-> 344 evidence summaries
-> human/operator review required
```

Automation may organize and validate review material. It must not choose
substantive review outcomes.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/REVIEW-IA-CANDIDATES-BATCH-00/task.yaml`
- `docs/planning/REVIEW_IA_CANDIDATES_BATCH_AUTHORITY_DECISION.md`
- `docs/operations/IA_SOURCE_OBSERVATION_CACHE_DELTA.md`
- `docs/operations/IA_CANDIDATE_INDEX_REFRESH.md`
- `docs/operations/IA_EVIDENCE_LEDGER_SUMMARY.md`
- `docs/reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md`
- `runtime/review/ledger.py`
- `tests/runtime/test_review_ledger.py`
- `control/audits/source_wave/ia_source_observation_cache_delta_v0/`
- `control/audits/source_wave/ia_candidate_index_refresh_v0/`
- `control/audits/source_wave/ia_evidence_ledger_summary_v0/`
- `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- `.eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json`
- `.eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json`
- `.aide/context/latest-context-packet.md` (present)
- `.aide/context/repo-map.json` (present)
- `.aide/context/test-map.json` (present)

## ALLOWED_PATHS

- `runtime/local/**`
- `runtime/review/**`
- `scripts/eureka_ia_candidate_review.py`
- `scripts/eureka_review.py` if using existing review wrapper behavior
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/review-batch/**`
- `contracts/review/**` only if using existing review shapes
- `contracts/evidence/**` only if using existing evidence shapes

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `.aide/queue/**` except final status reporting if repo convention requires it
- `docs/canon/**`
- `runtime/connectors/**`
- `runtime/gateway/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `examples/**`
- `evals/**`
- `release/**`
- `archive/**`
- `LICENSE.md`
- `LICENSE-SUMMARY.md`
- `NOTICE.md`
- public exposure, tunnel, hosting, or launch code
- source/provider expansion beyond existing IA source-observation, candidate, and evidence deltas
- reviewed-record materialization paths unless a separate future task authorizes them
- reviewed/master index refresh paths
- public-index mutation paths
- snapshot/public projection paths
- Workbench runtime unless separately authorized
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, downloaded files, payload bytes, and source AIDE repository state

## IMPLEMENTATION

- Read the review task packet and review ledger boundary first.
- Keep changes inside allowed paths.
- In prepare mode, write review batch items/templates only.
- In record-decisions mode, require explicit operator decision input.
- Preserve review as the truth boundary.
- Do not materialize reviewed records or rebuild indexes.

## MODES

### Prepare

- load candidate and evidence-summary deltas
- construct deterministic review items
- rank or group items for operator convenience only
- validate provenance, missing fields, orphan refs, and unsupported claims
- produce a review batch packet and blank decision templates
- write no review-ledger decisions
- make no truth changes

### Record Decisions

Available only when an explicit operator decision input file is supplied.

Required:

- named actor
- explicit decision per reviewed item included in the decision file
- evidence refs, source-observation refs, absence refs, fallback refs, or written rationale
- `local_only_confirmed: true` for promotion
- review-ledger decisions/events only

Forbidden:

- inferred missing decisions
- AI/model decisions treated as operator decisions
- implicit promotion from confidence or ranking
- bulk promote-all without explicit item-level review
- reviewed record creation
- reviewed/master/public index mutation

## SUPPORTED_DECISIONS

- `promote`
- `reject`
- `supersede`
- `mark_near_miss`
- `mark_need`
- `mark_policy_blocked`
- `request_more_evidence`

## OPERATOR_DECISION_INPUT

Expected shape:

```json
{
  "schema_version": "eureka.ia_candidate_review_decisions.v0",
  "batch_id": "...",
  "actor": "operator-name",
  "generated_at": "...",
  "decisions": [
    {
      "review_item_id": "...",
      "candidate_id": "...",
      "decision": "promote|reject|supersede|mark_near_miss|mark_need|mark_policy_blocked|request_more_evidence",
      "reason": "...",
      "evidence_refs": ["..."],
      "source_observation_refs": ["..."],
      "absence_refs": [],
      "fallback_refs": [],
      "supersedes_review_item_id": null,
      "local_only_confirmed": false
    }
  ]
}
```

Rules:

- `actor` is mandatory.
- Every recorded item decision must be explicit.
- `reason` is mandatory for `reject`, `supersede`, `mark_policy_blocked`, and `request_more_evidence`.
- `supersedes_review_item_id` is mandatory for `supersede`.
- At least one evidence/source/absence/fallback reference or written rationale is required.
- `promote` requires `local_only_confirmed: true`.
- Missing decisions remain pending and must not be inferred.
- A decision file may cover only a subset of the review batch.

## VALIDATION

- `python scripts/check_git_task_state.py --mode start-task --task-id REVIEW-IA-CANDIDATES-BATCH-00`
- future review-batch prepare command, once added
- future review-batch validate/status commands, once added
- `python -m unittest tests.runtime.test_review_ledger -v`
- `python -m unittest tests.operations.test_ia_evidence_ledger_summary -v`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `py -3 .aide/scripts/aide_lite.py validate`
- `git diff --check`

## EVIDENCE

- changed files
- task-state guard result
- AIDE pack/doctor/validate results
- focused review/evidence tests
- public-alpha and snapshot safety checks
- unresolved blockers and deferrals

## NON_GOALS

- No automatic promote/reject/supersede decision.
- No AI/model decision acceptance.
- No review decision inference from confidence scores.
- No reviewed-record creation.
- No reviewed/master-index mutation.
- No public-index mutation.
- No candidate-index-store mutation.
- No evidence-ledger-store mutation.
- No reviewed-index rebuild.
- No snapshot refresh.
- No public launch or exposure.
- No network/provider call, downloads, file fetch, Wayback replay, broad crawling, rights clearance claim, malware/binary safety claim, production-readiness claim, or license change.

## ACCEPTANCE

- Review batch preparation uses existing IA candidate and evidence-summary deltas.
- Prepare mode writes review items/templates only and records no decisions.
- Record-decisions mode is available only with explicit operator decision input.
- Decision input requires actor, item-level decision, references or rationale, and local-only confirmation for promotion.
- Reviewed-record/index materialization remains forbidden.
- Public exposure remains paused and license posture unchanged.
- Validation is run and recorded; full unittest discovery is not claimed unless separately authorized.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 8273
- approx_tokens: 2069
- budget_status: PASS
