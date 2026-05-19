# Latest Task Packet

## TASK

IA-PILOT-CLOSEOUT-01 - Internet Archive Metadata Pilot Closeout.

## PHASE

IA-PILOT-CLOSEOUT-01 completed as `PASS`.

## GOAL

Validate and summarize IA-00 through IA-07 as one bounded metadata-only
local-source vertical slice, then hand off to SYN-00 without starting SYN.

## WHY

IA-07 proved reviewed local index rebuild, search result, object packet, and
absence packet behavior in a temp explicit instance. Closeout records what now
works, what remains temp-instance-only, what remains disabled, what future
source-family work can reuse, and what must not be claimed.

## CONTEXT_REFS

- IA pilot closeout inventories
- IA pilot closeout audit pack
- IA-00 through IA-07 result inventories
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`

## ALLOWED_PATHS

- `control/inventory/ia_pilot_*.json`
- `control/policies/ia_*policy.json`
- `docs/operations/IA_METADATA_PILOT_CLOSEOUT.md`
- `docs/operations/IA_METADATA_PILOT_RUNBOOK.md`
- `docs/operations/POST_IA_SYN_ENTRY_PLAN.md`
- `docs/architecture/IA_METADATA_CONNECTOR_MODEL.md`
- `docs/reference/IA_METADATA_FIELD_MAPPING.md`
- `docs/reference/IA_SOURCE_CACHE_RECORD.md`
- `docs/reference/IA_EVIDENCE_RECORD.md`
- `docs/reference/IA_CANDIDATE_RECORD.md`
- `docs/reference/IA_REVIEW_ITEM.md`
- `docs/reference/IA_PROMOTION_PREVIEW.md`
- `docs/reference/IA_REVIEWED_LOCAL_RECORD.md`
- `scripts/validate_ia_pilot_closeout.py`
- `scripts/summarize_ia_pilot.py`
- `tests/operations/test_ia_pilot_closeout*.py`
- `tests/operations/test_ia_pilot_syn_handoff.py`
- `.aide/queue/IA-PILOT-CLOSEOUT-01/task.yaml`
- `.aide/queue/IA-TO-MAIN-PROMOTION-REVIEW/task.yaml`
- `.aide/queue/IA-TO-MAIN-PROMOTION-REVIEW/**`
- `.aide/queue/SYN-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/ia-pilot-closeout-01-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files, credentials, raw prompts, raw responses, and raw live IA
  response bodies
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

IA pilot closeout added:

- closeout input state, capability, validation, boundary, reuse, warning,
  blocker, result, and next-task inventories
- IA pilot closeout docs and post-IA SYN entry plan
- IA connector model closeout note
- closeout summary and validator scripts
- focused closeout tests
- closeout audit pack
- queue handoff to SYN-00 and IA-to-main promotion review

## NON_GOALS

- no new live IA call or source probe
- no broad Archive.org search, crawl, page scraping, or fanout
- no downloads, uploads, write APIs, S3 APIs, account APIs, or Wayback content
  replay
- no operator instance mutation
- no committed `data/public_index` mutation
- no master index mutation
- no extraction
- no model/provider calls
- no deployment
- no production/public launch claim
- no SYN implementation

## EVIDENCE

- `control/inventory/ia_pilot_closeout_result.json`
- `control/inventory/ia_pilot_capability_matrix.json`
- `control/inventory/ia_pilot_validation_matrix.json`
- `control/inventory/ia_pilot_boundary_matrix.json`
- `control/inventory/ia_pilot_reuse_matrix.json`
- `control/audits/ia-pilot-closeout-01-v0/`

## VALIDATION

- IA-00 through IA-07 validators
- `python scripts/validate_ia_pilot_closeout.py`
- IA pilot closeout focused tests
- architecture boundary check
- generated artifact cleanliness
- AIDE Lite doctor/validate/test/selftest/verify/review-pack/commit check

## ACCEPTANCE

- IA-00 through IA-07 validators pass.
- Closeout validator and focused tests pass.
- Capability, validation, boundary, reuse, warning, blocker, result, and next
  task inventories exist.
- Hard blockers and warnings are zero.
- The metadata vertical slice is marked complete.
- Full Archive.org integration is not claimed.
- Raw responses, operator instance, committed public index, master index,
  downloads, uploads, extraction, model/provider calls, deployment, production
  readiness, and public launch readiness remain forbidden.
- Queue points to SYN-00.

## OUTPUT_SCHEMA

Final result is recorded in `control/inventory/ia_pilot_closeout_result.json`
using `ia_pilot_closeout_result.v0`.

## TOKEN_ESTIMATE

- packet_chars: under 8000
- approximate_tokens: under 2000

## NEXT

Recommended next task: SYN-00 - Synthetic Query Foundry planning over
Local/HUNT/PLAY/IA.

Alternative: IA-TO-MAIN-PROMOTION-REVIEW - Promote IA metadata pilot baseline.
