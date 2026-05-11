# AIDE Latest Task Packet

## PHASE

H12-BUNDLE-02 - Retro and community archive fixture runtimes and normalizers

## GOAL

Continue H12 after policy-pack closure by adding fixture-only retro/community archive normalizers and replay outputs. H12-BUNDLE-02 must not enable live calls, downloads, extraction, execution, source sync, scraping, crawling, account/gated-source access, public/master index mutation, or truth acceptance. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

H12-BUNDLE-01 added policy-pack-only governance for retro/community archive sources and routed the wave to fixture runtime work. Fixture replay is the next controlled step before any future metadata-only live-probe envelope.

## CONTEXT_REFS

- `.aide/queue/H12-BUNDLE-02/task.yaml`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `control/audits/h12-bundle-01-retro-community-policy-packs-v0/`
- `control/inventory/source_packs/h12_retro_community_sources.json`
- `examples/connectors/h12_retro_community/`
- `docs/operations/H12_RETRO_COMMUNITY_FIXTURE_PLAN.md`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/`
- H12-BUNDLE-02 governed fixture-runtime artifacts only when that queue item is explicitly started from its task packet.

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
- `site/dist/**`
- `data/public_index/**`
- master-index roots
- local private roots
- ROM, ISO, disc-image, emulator, BIOS, vintage software download, installer, patch, crack/key/serial, gated-source account, forum-session, archive-extraction, hosted config, provider secret, or telemetry roots

## IMPLEMENTATION

- Read H12-BUNDLE-01 audit outputs first.
- Keep fixture work committed-fixture-only.
- Do not perform live calls or infer operator signoff.
- Keep all source/evidence/candidate/retro/community outputs as previews or candidates only.

## VALIDATION

- `python scripts/validate_h12_retro_community_policy_packs.py`
- `python scripts/check_architecture_boundaries.py`
- `python -m unittest discover -s tests -t .`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- H12-BUNDLE-01 audit pack under `control/audits/h12-bundle-01-retro-community-policy-packs-v0/`
- H12 source inventory under `control/inventory/source_packs/h12_retro_community_sources.json`
- H12 source-pack examples under `examples/connectors/h12_retro_community/`
- Validation command results and commit hash from the completed task.

## NON_GOALS

- No Eureka product behavior change.
- HUMAN-OBS-REVIEW-01 remains a parallel side-lane and is not advanced by this packet.
- No live source calls, network calls, model/provider calls, downloads, extraction, execution, acquisition actions, account/gated-source access, scraping, crawling, bypass, source sync, public/master index mutation, hosting, uploads, telemetry, or truth acceptance.

## ACCEPTANCE

- H12-BUNDLE-02 starts only after H12-BUNDLE-01 policy packs pass.
- Fixture runtime remains committed-fixture-only.
- J1 risky actions, K semantic/AI, and L wider clients remain deferred.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1100
- budget_status: PASS
