# AIDE Latest Task Packet

## PHASE

SOURCE_WAVE - IA-EVIDENCE-LEDGER-SUMMARY-00

## GOAL

Consume the governed IA source-observation cache delta and IA candidate-index
delta and produce a local evidence-summary ledger/delta for later review,
reviewed-index, snapshot, and local autonomous foundry tasks.

This is not public launch, public exposure, broad Archive.org crawling, a
downloader, Wayback replay, live public source fanout, review/promotion,
reviewed/master-index mutation, public-index mutation, candidate-index store
mutation, or source/provider expansion beyond the existing IA source-observation
and candidate delta path.

## WHY

Continue the local source-index path after `IA-CANDIDATE-INDEX-REFRESH-00` by
summarizing source observation and candidate refs into evidence support material
while preserving the review truth boundary.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/IA-EVIDENCE-LEDGER-SUMMARY-00/task.yaml`
- `control/audits/source_wave/ia_source_observation_cache_delta_v0/source_observation_cache_delta_report.json`
- `control/audits/source_wave/ia_candidate_index_refresh_v0/candidate_index_refresh_report.json`
- `control/audits/source_wave/ia_candidate_index_refresh_v0/authority_closeout.json`
- `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- `.eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json`
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
- `.aide/prompts/compact-task.md`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/local-state.yaml`

## ALLOWED_PATHS

- `runtime/local/**`
- `scripts/eureka_evidence_ledger_summary.py`
- `scripts/eureka_index.py` if the repo already uses it for local source-index summaries
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/evidence-ledger/**`
- `contracts/source/**` only for a narrow source/candidate/evidence bridge schema
- `contracts/evidence/**` only if an existing repo convention supports narrow evidence contracts

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
- source/provider expansion beyond the existing IA source-observation and candidate deltas
- reviewed/master index mutation paths
- public-index mutation paths
- candidate-index store mutation paths
- review/promotion mutation paths
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, downloaded files, payload bytes, and source AIDE repository state

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Treat source observations, candidates, and evidence summaries as unreviewed support material.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py validate`
- `python scripts/check_git_task_state.py --mode start-task --task-id IA-EVIDENCE-LEDGER-SUMMARY-00`
- future implementation command for evidence-ledger summary, once added
- future strict validation/status commands for the evidence-ledger delta, once added
- focused evidence/source-wave tests, once added
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
- verifier result when available
- compact packet size and budget status
- unresolved risks and deferrals

## NON_GOALS

- No public launch, public exposure, tunnel/provider work, deployment, production-readiness claim, public-launch claim, main promotion, force-push, or history rewrite.
- No downloads, file fetches, Wayback replay, broad IA crawling, provider/network call during evidence-ledger summary, or public live source fanout.
- No reviewed/master truth mutation, public-index mutation, candidate-index store mutation, review/promotion mutation, rights clearance claim, malware/binary safety claim, or license posture change.
- No source/provider expansion beyond the existing IA source-observation and candidate deltas.

## ACCEPTANCE

- Evidence-ledger summary consumes the governed IA source-observation cache delta and candidate-index delta.
- Evidence output is a local evidence-summary ledger/delta only.
- No network, downloads, file fetch, Wayback replay, public fanout, reviewed/master mutation, public-index mutation, candidate-index store mutation, or review/promotion mutation occurs.
- Tracked audit summary exists under `control/audits/source_wave/`.
- Validation is run and recorded; full unittest discovery is not claimed unless separately authorized.
- No secrets, raw prompt logs, local caches, downloaded payloads, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and
`NEXT`. Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6880
- approx_tokens: 1720
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
