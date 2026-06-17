# AIDE Latest Task Packet

## PHASE

SOURCE_WAVE - IA-SOURCE-OBSERVATION-CACHE-DELTA-00

## GOAL

Materialize the completed IA metadata smoke output into a governed local
source-observation cache delta that can be replayed, audited, diffed, and later
used by evidence, candidate-index, review, snapshot, and local autonomous
foundry tasks.

This is not public launch, public exposure, broad Archive.org crawling, a
downloader, Wayback replay, live public source fanout, reviewed/master-index
mutation, public-index mutation, or source/provider expansion beyond the IA
metadata smoke path.

## WHY

Continue AIDE token survival by using repo-local context refs, compact objectives, deterministic validation, and evidence packets instead of long chat history.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/IA-SOURCE-OBSERVATION-CACHE-DELTA-00/task.yaml`
- `control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/authority_closeout.json`
- `control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/repo-snapshot.json` (present)
- `.aide/context/repo-map.json` (present)
- `.aide/context/repo-map.md` (present)
- `.aide/context/test-map.json` (present)
- `.aide/context/context-index.json` (present)
- `.aide/context/latest-context-packet.md` (present)
- `.aide/repo/latest-repo-intelligence.md` (present)
- `.aide/repo/file-inventory.json` (present)
- `.aide/reports/file-quality-summary.md` (present)
- `.aide/reports/file-quality-ledger.json` (present)
- `.aide/refactors/latest-refactor-readiness.md` (present)
- `.aide/refactors/latest-refactor-plan.example.json` (present)
- `.aide/routing/latest-route-decision.json` (present)
- `.aide/routing/latest-route-decision.md` (present)
- `.aide/cache/latest-cache-keys.json` (present)
- `.aide/cache/latest-cache-keys.md` (present)
- `.aide/prompts/compact-task.md`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/local-state.yaml`

## ALLOWED_PATHS

- `docs/operations/**`
- `runtime/local/**`
- `scripts/eureka_source_observation_cache.py`
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/source-observation-cache/**`
- `contracts/source/**` only for a narrow source-observation cache schema

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
- Workbench runtime unless an explicitly reviewed follow-up authorizes it
- public exposure, tunnel, hosting, or launch code
- source/provider expansion beyond the IA metadata smoke path
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, downloaded files, payload bytes, and source AIDE repository state

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py validate`
- `python scripts/eureka_source_observation_cache.py build-delta --source ia_metadata --smoke-report control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json --out .eureka/source-wave/ia-metadata/source-observation-cache/latest`
- `python scripts/eureka_source_observation_cache.py validate --delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json --strict`
- `python scripts/eureka_source_observation_cache.py status --delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- `python -m unittest tests.operations.test_ia_source_observation_cache_delta`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/eureka_test_select.py --changed --failed-first --json` if available and relevant
- `git diff --check`

## COMMITS

- Commit coherent subdeliverables with verbose bodies.
- Stop at review gates.

## EVIDENCE

- changed files
- validation commands and results
- verifier result
- review packet path and result when review-pack is available
- advisory route decision path and result when Q17 routing is available
- compact packet size and budget status
- unresolved risks and deferrals

## NON_GOALS

- No public launch, public exposure, tunnel/provider work, deployment, production-readiness claim, public-launch claim, main promotion, force-push, or history rewrite.
- No downloads, file fetches, Wayback replay, broad IA crawling, live provider call during cache-delta build, or public live source fanout.
- No reviewed/master truth mutation, public-index mutation, rights clearance claim, malware/binary safety claim, or license posture change.
- No source/provider expansion beyond the completed IA metadata smoke path.

## ACCEPTANCE

- Source observation cache delta builds from the completed IA smoke report.
- Strict delta validation passes and status command reports deterministic counts.
- Tracked audit summary exists under `control/audits/source_wave/`.
- No network, downloads, file fetch, Wayback replay, public fanout, reviewed/master mutation, or public-index mutation occurs.
- Validation is run and recorded; full unittest discovery is not claimed unless separately authorized.
- No secrets, raw prompt logs, local caches, downloaded payloads, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6655
- approx_tokens: 1664
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
