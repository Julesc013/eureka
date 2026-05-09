# AIDE Latest Task Packet

## PHASE

H0-BUNDLE-02 - Connector interface, fixture replay, and live-probe envelope

## GOAL

Build on H0-BUNDLE-01 by defining the reusable Eureka connector-family
interface, fixture/replay harness, policy evaluator, and live-probe envelope
that future H1 metadata sources can share.

## WHY

H0-BUNDLE-01 added Source OS registry v2, source records, family taxonomy,
capability ladder, D0-D5 index-depth vocabulary, trust lanes, access modes,
operation policy, approval gates, no-live-call policy, source examples,
validators, tests, and audit evidence.

The IA connector lane remains the reference pattern. IA-BUNDLE-02 stayed
blocked by policy for live access, and IA-BUNDLE-03 used fixture-equivalent
blocked outputs for review integration and quality-delta rehearsal.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane. IA-APPROVAL-01 remains an
operator-gated side-lane for one possible IA metadata live probe. Neither
side-lane authorizes broad H-wave source fanout.

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
- `control/audits/h0-bundle-01-source-os-foundation-v0/`
- `contracts/sources/source_registry.v2.json`
- `contracts/sources/source_record.v2.json`
- `contracts/sources/source_policy.v0.json`
- `contracts/sources/source_operation_policy.v0.json`
- `contracts/sources/source_index_depth.v0.json`
- `control/inventory/sources/source_family_registry.json`
- `control/inventory/sources/source_capability_ladder.json`
- `control/inventory/sources/source_operation_policy.json`
- `control/inventory/sources/source_approval_gate_policy.json`
- `docs/architecture/SOURCE_OPERATING_SYSTEM.md`
- `docs/operations/SOURCE_POLICY_GATES.md`
- `docs/operations/SOURCE_EXPANSION_NO_LIVE_CALL_POLICY.md`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H0-BUNDLE-02/**`
- `.aide/reports/eureka-repo-health.md`
- `.aide/reports/eureka-repo-health.json`
- `control/audits/h0-bundle-02-connector-interface-fixture-replay-v0/**`
- `control/inventory/connectors/source_connector_interface_policy.json`
- `control/inventory/connectors/source_fixture_replay_policy.json`
- `control/inventory/connectors/source_live_probe_envelope_policy.json`
- `control/inventory/connectors/source_policy_evaluator_policy.json`
- `contracts/connectors/source_connector_interface.v0.json`
- `contracts/connectors/source_fixture_replay.v0.json`
- `contracts/connectors/source_live_probe_envelope.v0.json`
- `docs/architecture/SOURCE_CONNECTOR_INTERFACE_MODEL.md`
- `docs/operations/SOURCE_FIXTURE_REPLAY_POLICY.md`
- `docs/operations/SOURCE_LIVE_PROBE_ENVELOPE.md`
- `docs/reference/SOURCE_CONNECTOR_INTERFACE.md`
- `examples/connectors/source_os_fixture_replay/**`
- `scripts/validate_source_connector_interface_foundation.py`
- `tests/contracts/test_source_connector_interface_foundation.py`
- `tests/operations/test_source_connector_interface_scripts.py`

If H0-BUNDLE-02 needs a narrow runtime helper, create or update the queue task
with exact file paths before editing. Do not use broad runtime scopes.
Proceed without changing Eureka product behavior.

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
- `connectors/**`
- `crates/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- local private-state roots
- raw prompt logs, credentials, provider keys, or cache contents

## IMPLEMENTATION

- Define the connector-family interface around Source OS source records and
  policy gates.
- Define fixture replay inputs, outputs, and deterministic validation.
- Define live-probe envelope requirements while keeping live calls disabled by
  default.
- Define a policy evaluator that can fail closed before network access.
- Reuse IA as a reference pattern, not as a special one-off connector.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/check_architecture_boundaries.py`
- H0-BUNDLE-02-specific validators and tests added by the future task
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- H0-BUNDLE-01 evidence lives under
  `control/audits/h0-bundle-01-source-os-foundation-v0/`.
- IA-BUNDLE-03 evidence lives under
  `control/audits/ia-bundle-03-review-integration-quality-delta-v0/`.
- IA-BUNDLE-02 remains blocked unless IA-APPROVAL-01 makes an explicit
  operator policy decision.
- Do not paste long chat history when compact packets and audit packs are
  sufficient.

## NON_GOALS

- Do not perform new IA live calls or any other live source calls.
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

- Connector-family interface contracts and policies exist.
- Fixture replay policy and examples exist.
- Live-probe envelope is defined and fails closed by default.
- Policy evaluator requirements are documented and tested.
- No live source access, source sync, downloads, public/master index mutation,
  truth acceptance, or product behavior change is enabled.

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

approx_tokens: 1500
