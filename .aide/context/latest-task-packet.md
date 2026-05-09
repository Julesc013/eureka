# AIDE Latest Task Packet

## PHASE

H0-BUNDLE-02 - Connector interface, fixture replay, and live-probe envelope

## GOAL

Add the reusable Source OS connector-interface layer: generic connector
contracts, connector family registry, fixture replay harness, output envelopes,
live-probe envelopes, policy evaluation, docs, examples, tests, and audit
evidence. This task must not enable live source access.

## WHY

H0-BUNDLE-01 created source registry v2, source families, capabilities, trust
lanes, access modes, operation policy, and approval gates. H0-BUNDLE-02 turns
that source vocabulary into a repeatable connector framework so future H1/H2
connectors are policy-governed instead of one-off site integrations.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/H0-BUNDLE-02/task.yaml`
- `control/audits/h0-bundle-01-source-os-foundation-v0/`
- `control/audits/ia-bundle-03-review-integration-quality-delta-v0/`
- `contracts/sources/source_record.v2.json`
- `control/inventory/sources/source_family_registry.json`
- `control/inventory/sources/source_operation_policy.json`

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H0-BUNDLE-02/**`
- `control/audits/h0-bundle-02-connector-interface-replay-v0/**`
- `control/inventory/connectors/connector_*_policy.json`
- `control/inventory/connectors/connector_family_registry.json`
- `control/inventory/connectors/live_probe_envelope_policy.json`
- `contracts/connectors/source_connector_interface.v0.json`
- `contracts/connectors/source_connector_capability.v0.json`
- `contracts/connectors/source_connector_fixture_replay.v0.json`
- `contracts/connectors/source_connector_output_envelope.v0.json`
- `contracts/connectors/live_probe_request.v0.json`
- `contracts/connectors/live_probe_result.v0.json`
- `contracts/connectors/connector_policy_evaluation.v0.json`
- `contracts/connectors/connector_family.v0.json`
- `runtime/connectors/core/**`
- `examples/connectors/core/**`
- `scripts/run_connector_fixture_replay.py`
- `scripts/evaluate_connector_policy.py`
- `scripts/summarize_connector_families.py`
- `scripts/validate_connector_interface_foundation.py`
- `tests/connectors/test_connector_interface_foundation.py`
- `tests/operations/test_connector_interface_foundation_scripts.py`
- `docs/reference/SOURCE_CONNECTOR_INTERFACE.md`
- `docs/reference/CONNECTOR_FIXTURE_REPLAY_CONTRACT.md`
- `docs/reference/LIVE_PROBE_ENVELOPE_CONTRACT.md`
- `docs/reference/CONNECTOR_POLICY_EVALUATION_CONTRACT.md`
- `docs/architecture/CONNECTOR_INTERFACE_MODEL.md`
- `docs/architecture/CONNECTOR_FIXTURE_REPLAY_MODEL.md`
- `docs/operations/CONNECTOR_POLICY_EVALUATION.md`
- `docs/operations/CONNECTOR_NO_LIVE_CALL_POLICY.md`

## FORBIDDEN_PATHS

- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- `.git/**`
- `.env`
- `.env.*`
- `secrets/**`
- `.aide.local/**`

The active queue task narrows the H0-BUNDLE-02 exceptions above. Work proceeds
without changing Eureka product behavior.

## IMPLEMENTATION

- Define connector interface, capability, family, fixture replay, output
  envelope, live-probe, and policy-evaluation contracts.
- Add no-network helper modules under `runtime/connectors/core/**`.
- Add CLIs for fixture replay, policy evaluation, family summaries, and
  validation.
- Add examples and generated audit evidence for offline replay and blocked live
  probes.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_connector_interface_foundation.py`
- `python -m unittest tests.connectors.test_connector_interface_foundation`
- `python -m unittest tests.operations.test_connector_interface_foundation_scripts`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- Audit pack: `control/audits/h0-bundle-02-connector-interface-replay-v0/`
- Queue task: `.aide/queue/H0-BUNDLE-02/task.yaml`
- Generated samples under the audit pack plus `examples/connectors/core/**`

## NON_GOALS

- No live source calls, API calls, source sync, downloads, scraping, crawling,
  public query fanout, model calls, public/master index mutation, evidence or
  candidate acceptance, rights clearance, malware safety, installability, or
  production-readiness claims.

## ACCEPTANCE

- Contracts, policies, runtime helpers, scripts, examples, docs, tests, and
  audit evidence exist and validate offline.
- No new live source access or product behavior change is enabled.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED`, `VALIDATION`, `RISKS`, and
`NEXT TASK`.

## TOKEN_ESTIMATE

approx_tokens: 1500
