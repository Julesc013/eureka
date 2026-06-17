# AIDE Latest Task Packet

## PHASE

SOURCE_WAVE - IA-CANDIDATE-INDEX-REFRESH-00

## GOAL

Consume the governed IA source-observation cache delta and produce a local
candidate-index delta or dry-run preview for later evidence, review, snapshot,
and local autonomous foundry tasks.

This is not public launch, public exposure, broad Archive.org crawling, a
downloader, Wayback replay, live public source fanout, evidence-ledger
materialization, reviewed/master-index mutation, public-index mutation, or
source/provider expansion beyond the existing IA source-observation cache delta.

## WHY

Continue the local source-index path after `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`
by deriving provisional candidate-index material from governed source
observations while preserving the review truth boundary.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/IA-CANDIDATE-INDEX-REFRESH-00/task.yaml`
- `control/audits/source_wave/ia_source_observation_cache_delta_v0/source_observation_cache_delta_report.json`
- `control/audits/source_wave/ia_source_observation_cache_delta_v0/authority_closeout.json`
- `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
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
- `scripts/eureka_candidate_index_refresh.py`
- `scripts/eureka_index.py` if the repo already uses it for local candidate index behavior
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/candidate-index/**`
- `contracts/source/**` only for a narrow source-observation/candidate bridge schema
- `contracts/index/**` only if an existing repo convention supports narrow index contracts

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
- source/provider expansion beyond the existing IA source-observation cache delta
- reviewed/master index mutation paths
- public-index mutation paths
- raw provider credentials, API keys, local caches, raw prompt logs, raw responses, downloaded files, payload bytes, and source AIDE repository state

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Treat source observations and derived candidates as unreviewed, provisional material.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py validate`
- `python scripts/check_git_task_state.py --mode start-task --task-id IA-CANDIDATE-INDEX-REFRESH-00`
- future implementation command for candidate-index refresh, once added
- future strict validation/status commands for the candidate-index delta, once added
- focused candidate-index/source-wave tests, once added
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
- No downloads, file fetches, Wayback replay, broad IA crawling, provider/network call during candidate-index refresh, or public live source fanout.
- No reviewed/master truth mutation, public-index mutation, evidence-ledger materialization, rights clearance claim, malware/binary safety claim, or license posture change.
- No source/provider expansion beyond the existing IA source-observation cache delta.

## ACCEPTANCE

- Candidate-index refresh consumes the governed IA source-observation cache delta.
- Candidate-index output is a local delta or dry-run preview only.
- No network, downloads, file fetch, Wayback replay, public fanout, reviewed/master mutation, public-index mutation, or evidence-ledger mutation occurs.
- Tracked audit summary exists under `control/audits/source_wave/`.
- Validation is run and recorded; full unittest discovery is not claimed unless separately authorized.
- No secrets, raw prompt logs, local caches, downloaded payloads, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and
`NEXT`. Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6748
- approx_tokens: 1687
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
