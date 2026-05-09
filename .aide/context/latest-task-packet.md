# AIDE Latest Task Packet

## PHASE

IA-BUNDLE-02 - IA bounded metadata live probe

## GOAL

Add the bounded Internet Archive metadata live-probe envelope without changing
Eureka product behavior. The runtime may perform at most one approved metadata
endpoint read for one approved identifier, but the current committed policy
state blocks the live call and produces offline blocked evidence instead.

## WHY

IA-BUNDLE-01 returned `pass_with_warnings` and added the fixture-only IA
metadata foundation. IA-BUNDLE-02 tests the first live-source boundary while
preserving the doctrine that IA metadata is a source observation, not truth.
Because source, User-Agent/contact, rate, cache, kill-switch, and identifier
approvals remain pending, the correct next development result is a fail-closed
blocked preflight and an operator approval handoff.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane. It is review-gated,
human-operated, and does not block IA-BUNDLE-02 preflight or the
IA-APPROVAL-01 operator decision.

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
- `control/audits/ia-bundle-01-metadata-connector-foundation-v0/`
- `contracts/connectors/internet_archive_metadata_connector.v0.json`
- `contracts/connectors/source_connector_fixture.v0.json`
- `runtime/connectors/internet_archive/metadata_normalizer.py`
- `runtime/connectors/internet_archive/fixture_loader.py`
- `docs/reference/LOCAL_SOURCE_CACHE_RUNTIME.md`
- `docs/reference/LOCAL_EVIDENCE_LEDGER_RUNTIME.md`
- `docs/reference/SOURCE_CACHE_TO_EVIDENCE_BRIDGE_RUNTIME.md`
- `docs/reference/LOCAL_REVIEW_QUEUE_RUNTIME.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/queue/index.yaml`
- `.aide/queue/IA-BUNDLE-02/**`
- `control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/**`
- `control/inventory/connectors/internet_archive_live_probe_policy.json`
- `control/inventory/connectors/internet_archive_live_probe_allowed_identifiers.json`
- `control/inventory/connectors/internet_archive_live_probe_output_policy.json`
- `control/inventory/connectors/internet_archive_live_probe_path_policy.json`
- `control/inventory/connectors/internet_archive_live_probe_review_policy.json`
- `control/inventory/connectors/internet_archive_live_probe_truth_policy.json`
- `docs/architecture/IA_METADATA_LIVE_PROBE_MODEL.md`
- `docs/operations/IA_METADATA_LIVE_PROBE_REVIEW.md`
- `docs/reference/IA_METADATA_LIVE_PROBE.md`
- `docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR.md`
- `examples/connectors/internet_archive/live_probe/**`
- `runtime/connectors/README.md`
- `runtime/connectors/internet_archive/__init__.py`
- `runtime/connectors/internet_archive/live_metadata_probe.py`
- `scripts/run_ia_metadata_live_probe.py`
- `scripts/validate_ia_metadata_live_probe.py`
- `tests/connectors/test_internet_archive_live_probe.py`
- `tests/operations/test_ia_metadata_live_probe_scripts.py`

The reviewed IA-BUNDLE-02 prompt explicitly opens only the live-probe boundary
paths above. This packet does not authorize broad runtime edits, product search
changes, source sync, downloads, hosting, or index mutation.

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
- `control/inventory/sources/**`
- local private-state roots
- raw prompt logs, credentials, provider keys, or cache contents

## IMPLEMENTATION

- Preserve IA-BUNDLE-00 and IA-BUNDLE-01 evidence.
- Add live-probe policy, allowed identifiers, output, path, review, and truth
  policy records.
- Add `runtime/connectors/internet_archive/live_metadata_probe.py` with
  standard-library-only policy validation and one-request fetch logic.
- Add `scripts/run_ia_metadata_live_probe.py` with default offline preflight
  and explicit `--live` gating.
- Add `scripts/validate_ia_metadata_live_probe.py` as an offline validator.
- Add examples, docs, tests, and the IA-BUNDLE-02 audit pack.
- Keep the current committed live probe blocked unless every policy gate is
  approved.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_ia_metadata_connector_foundation.py`
- `python scripts/validate_ia_metadata_live_probe.py`
- `python scripts/run_ia_metadata_live_probe.py --identifier eureka-software-fixture --check`
- `python -m unittest tests.connectors.test_internet_archive_live_probe`
- `python -m unittest tests.operations.test_ia_metadata_live_probe_scripts`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- IA-BUNDLE-02 evidence lives under
  `control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/`.
- The blocked generated result must show `attempted: false`,
  `request_count: 0`, and `network_used: false`.
- Do not paste long chat history when these compact packets and audit packs are
  sufficient.

## NON_GOALS

- Do not broad-search Internet Archive.
- Do not use advancedsearch.
- Do not fetch item files, download files, scrape HTML, crawl, or follow
  arbitrary URLs.
- Do not perform public-query live fanout or source sync.
- Do not call models, providers, browser automation, uploads, accounts,
  telemetry, hosting, or native project tooling.
- Do not mutate source cache runtime state, evidence ledger runtime state,
  review queue runtime state, public index, or master index.
- Do not accept source records, evidence, candidates, or public truth.
- Do not claim rights clearance, malware safety, verified installability, or
  production readiness.

## ACCEPTANCE

- Live probe runtime, CLI, validator, policies, examples, docs, tests, and
  audit pack exist.
- Validator default mode is offline.
- Current policy blocks live call before network access.
- Mocked tests cover the approved one-request path.
- HUMAN-OBS-REVIEW-01 remains documented as a parallel side-lane.
- No Eureka product behavior change occurs.
- Next recommended task is `IA-APPROVAL-01` unless an operator separately
  approves the live probe.

## OUTPUT_SCHEMA

Return the final response with:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `LIVE_PROBE`
- `CHANGED`
- `VALIDATION`
- `RISKS`
- `NEXT TASK`

## TOKEN_ESTIMATE

approx_tokens: 1500
