# AIDE Latest Task Packet

## PHASE

H0-BUNDLE-01 - Source OS registry and policy foundation

## GOAL

Lift the repeatable IA connector pattern into a shared Source Operating System
foundation before broad H1 connector expansion.

## WHY

IA-BUNDLE-03 produced review integration, quality-delta, connector postmortem,
and H0 readiness evidence from committed IA-BUNDLE-02 blocked outputs. No new
IA live call was made. The live IA approval decision remains an operator-gated
side-lane, while the main development lane can proceed to H0.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane. IA-APPROVAL-01 remains an
operator side-lane for the one approved IA metadata probe. Neither side-lane
unblocks broad source fanout or source sync.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/sync-baseline-01-canonical-main-v0/`
- `control/audits/track-b-23-integration-audit-v0/`
- `control/audits/ia-bundle-00-readiness-polish-v0/`
- `control/audits/ia-bundle-01-metadata-connector-foundation-v0/`
- `control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/`
- `control/audits/ia-bundle-03-review-integration-quality-delta-v0/`
- `docs/architecture/IA_METADATA_CONNECTOR_MODEL.md`
- `docs/architecture/IA_METADATA_LIVE_PROBE_MODEL.md`
- `docs/architecture/IA_METADATA_REVIEW_INTEGRATION_MODEL.md`
- `docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR.md`
- `docs/reference/IA_METADATA_LIVE_PROBE.md`
- `docs/reference/IA_METADATA_REVIEW_INTEGRATION.md`
- `docs/reference/LOCAL_SOURCE_CACHE_RUNTIME.md`
- `docs/reference/LOCAL_EVIDENCE_LEDGER_RUNTIME.md`
- `docs/reference/LOCAL_REVIEW_QUEUE_RUNTIME.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H0-BUNDLE-01/**`
- `control/audits/h0-bundle-01-source-os-registry-policy-foundation-v0/**`
- `control/inventory/source_os/**`
- `docs/architecture/SOURCE_OS_MODEL.md`
- `docs/operations/SOURCE_OS_POLICY.md`
- `docs/reference/SOURCE_OS_REGISTRY.md`
- `tests/operations/test_h0_source_os_foundation.py`
- `scripts/validate_h0_source_os_foundation.py`

This next packet is a planning handoff only. It does not authorize broad live
source probes, downloads, hosted source sync, public fanout, public-index
mutation, or master-index mutation.
It must proceed without changing Eureka product behavior.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `.env.*`
- `secrets/**`
- `.aide.local/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `runtime/**`
- `contracts/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- local private-state roots
- raw prompt logs, credentials, provider keys, or cache contents

## IMPLEMENTATION

- Define source family registry and capability ladder vocabulary.
- Define source policy gate and fixture/replay harness requirements.
- Define live-probe envelope requirements without enabling live probes.
- Define future coverage ledger and connector scorecard foundations.
- Preserve IA as the reference connector pattern, not a one-off site adapter.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/check_architecture_boundaries.py`
- H0-specific validators and tests added by the future task
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- IA-BUNDLE-03 evidence lives under
  `control/audits/ia-bundle-03-review-integration-quality-delta-v0/`.
- IA-BUNDLE-02 remains blocked unless IA-APPROVAL-01 makes an explicit operator
  policy decision.
- Do not paste long chat history when compact packets and audit packs are
  sufficient.

## NON_GOALS

- Do not perform new IA live calls.
- Do not broad-search Internet Archive or any other source.
- Do not fetch item files, download files, scrape HTML, crawl, or follow
  arbitrary URLs.
- Do not perform public-query live fanout or source sync.
- Do not mutate source cache runtime state, evidence ledger runtime state,
  review queue runtime state, public index, or master index.
- Do not accept source records, evidence, candidates, packs, or public truth.
- Do not claim rights clearance, malware safety, verified installability,
  production readiness, external superiority, or exhaustive coverage.

## ACCEPTANCE

- H0 source registry, capability ladder, policy gate, replay harness, live
  envelope, coverage ledger, connector scorecard, tests, validator, and audit
  evidence exist.
- No source connector expansion or live probe is enabled by H0-BUNDLE-01.
- IA-APPROVAL-01 and HUMAN-OBS-REVIEW-01 remain documented side-lanes.

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
