# AIDE Latest Task Packet

## PHASE

IA-BUNDLE-01 - IA metadata connector foundation

## GOAL

Prepare the first Internet Archive metadata connector foundation bundle after
IA-BUNDLE-00 readiness polish. The main development lane proceeds to IA source
policy, operator gate decisions, fixture metadata normalization, and connector
pattern groundwork without live IA calls unless a later explicit approval
subgate permits them.

## WHY

Track B is complete enough for first connector approval and the canonical sync
baseline supersedes the older active-merge and full-test warnings. The active
development lane now needs IA connector foundation work, while
HUMAN-OBS-REVIEW-01 continues as a parallel side-lane. OBS review remains
review-gated and does not block IA preflight or foundation work.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/sync-baseline-01-canonical-main-v0/`
- `control/audits/track-b-23-integration-audit-v0/`
- `control/audits/ia-bundle-00-readiness-polish-v0/`
- `docs/roadmap/TRACK_EXECUTION_PLAN.md`
- `docs/decisions/ADR-eureka-track-order.md`
- `docs/reference/LOCAL_SOURCE_CACHE_RUNTIME.md`
- `docs/reference/LOCAL_EVIDENCE_LEDGER_RUNTIME.md`
- `docs/reference/SOURCE_CACHE_TO_EVIDENCE_BRIDGE_RUNTIME.md`
- `docs/reference/LOCAL_REVIEW_QUEUE_RUNTIME.md`
- `docs/reference/CANDIDATE_PROMOTION_DRY_RUN.md`
- `docs/reference/REVIEWED_PUBLIC_INDEX_REBUILD_CONTRACT.md`
- `contracts/evidence/`
- `contracts/evidence_ledger/`
- `control/inventory/evidence_ledger/`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/policies/commit-messages.yaml`
- `.aide/queue/IA-BUNDLE-01/**`
- `.aide/scripts/aide_lite.py`
- `contracts/README.md`
- `contracts/connectors/internet_archive_metadata_connector.v0.json`
- `contracts/connectors/source_connector_fixture.v0.json`
- `control/audits/ia-bundle-01-metadata-connector-foundation-v0/**`
- `control/inventory/connectors/internet_archive_*_policy.json`
- `docs/architecture/IA_METADATA_CONNECTOR_MODEL.md`
- `docs/operations/IA_METADATA_FIXTURE_REPLAY.md`
- `docs/operations/IA_METADATA_NO_LIVE_CALL_POLICY.md`
- `docs/operations/IA_METADATA_SOURCE_POLICY.md`
- `docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR.md`
- `examples/connectors/internet_archive/**`
- `runtime/connectors/README.md`
- `runtime/connectors/internet_archive/**`
- `scripts/normalize_ia_metadata_fixture.py`
- `scripts/validate_ia_metadata_connector_foundation.py`
- `tests/connectors/test_internet_archive_metadata_foundation.py`
- `tests/operations/test_ia_metadata_connector_foundation.py`

The reviewed IA-BUNDLE-01 task prompt explicitly opens the specific connector,
contract, fixture, policy, audit, validator, and test paths above. This packet
does not authorize broad runtime or product behavior edits outside those
fixture-only foundation paths.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- source/evidence/master-index records
- generated static artifacts
- local private-state roots
- raw prompt logs, credentials, provider keys, or cache contents

Specific IA-BUNDLE-01 files listed in `ALLOWED_PATHS` are the only exceptions
to the broad `runtime/**` and `contracts/**` guards for this task.

## IMPLEMENTATION

- Start from a fresh task branch after the Git task-state guard passes.
- Treat `control/audits/ia-bundle-00-readiness-polish-v0/` as the IA readiness
  handoff.
- Draft source policy, endpoint posture, User-Agent/contact, rate-limit,
  timeout, retry, cache TTL, and kill-switch decisions.
- Add fixture-only IA metadata normalization, fixture replay examples, source
  cache preview mapping, evidence candidate preview mapping, validators, and
  tests.
- Preserve the source operating system pattern: source family, policy gate,
  fixture/replay harness, live-probe envelope, source cache, evidence
  candidate bridge, review queue, future coverage ledger, and future connector
  scorecard.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_ia_readiness_polish.py`
- IA-BUNDLE-01 task-specific validators and tests
- `python scripts/check_architecture_boundaries.py` if Python layering changes
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- IA-BUNDLE-00 evidence remains under
  `control/audits/ia-bundle-00-readiness-polish-v0/`.
- Preserve sync baseline evidence under
  `control/audits/sync-baseline-01-canonical-main-v0/`.
- Preserve Track B evidence under
  `control/audits/track-b-23-integration-audit-v0/`.
- Do not paste long chat history when these compact packets and audit packs are
  sufficient.

## NON_GOALS

- Do not call the Internet Archive.
- Do not perform live probes, source sync, broad crawling, downloads, uploads,
  accounts, telemetry, hosting, pack import, or hosted review.
- Do not enable a connector runtime.
- Do not mutate the public index or master index.
- Do not accept evidence, candidates, or public truth.
- Do not implement H0 in IA-BUNDLE-01 unless a later reviewed task explicitly
  expands scope.
- No Eureka product behavior change is authorized by this compact packet alone;
  any product contract edit requires the reviewed IA-BUNDLE-01 task scope.

## ACCEPTANCE

- Main development lane points to IA-BUNDLE-01.
- HUMAN-OBS-REVIEW-01 remains documented as a parallel side-lane.
- IA-BUNDLE-00 audit pack is available as readiness evidence.
- No IA source access, connector runtime, live probe, source sync, or
  index/master-index mutation is approved by this packet.
- Validation is run and recorded for the actual IA-BUNDLE-01 scope.

## OUTPUT_SCHEMA

Return the final response with:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `CHANGED`
- `VALIDATION`
- `RISKS`
- `NEXT TASK`

## TOKEN_ESTIMATE

approx_tokens: 1100
