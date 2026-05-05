# Public Search Ranking Local Dry-Run Runtime

P107 adds a local dry-run ranking runtime for approved synthetic public-search result fixtures. It is a report-only tool for seeing how explicit evidence-weighted and compatibility-aware factors would order results.

## Scope

Implemented:

- approved fixture loading
- explicit factor extraction
- evidence-weighted and compatibility-aware factor summaries
- deterministic proposed order
- current-order fallback
- public and audit explanation summaries
- JSON report generation and validation

Not implemented:

- public search integration
- hosted ranking runtime
- route, response, result-card, or order changes
- hidden scoring, result suppression, model calls, AI reranking, telemetry, popularity, user-profile, or ad signals
- source-cache/evidence-ledger reads or writes
- candidate or index mutation

## Input Model

Use `--all-examples` or an approved `--example-root` under:

- `examples/public_search_ranking_dry_run`
- `examples/evidence_weighted_ranking`
- `examples/compatibility_aware_ranking`

The CLI rejects arbitrary paths, absolute private paths, URLs, connector params, store/index/database paths, telemetry, user profiles, ad signals, model providers, mutation, promotion, suppression, and hosted/public write flags.

## Output Model

The JSON report includes current order, proposed dry-run order, fallback order, factor lists, explanation summaries, conflict/gap visibility counts, eval-gate summary, warnings, errors, and hard booleans.

## Ranking Factors

Factors are categorical and explicit. The runtime emits evidence, provenance, source posture, intrinsic identifier, compatibility, platform, architecture, runtime dependency, representation, member access, freshness, conflict, uncertainty, candidate, rights/risk, action safety, gap transparency, merge/grouping, identity, and manual-review factors.

Hidden scores are forbidden.

## Evidence And Compatibility

Evidence is not truth. Strong evidence covers intrinsic identifiers, checksums, and reviewed refs. Medium evidence covers recorded/source-backed metadata. Weak evidence covers lexical or alias-only matches.

Compatibility covers platform, architecture, runtime/dependency, and hardware hints. Unknown compatibility remains visible. No installability or dependency-safety claim is made.

## Boundaries

Public search does not call this runtime. Source/evidence refs in examples are synthetic labels only. Candidates are not promoted. No public, local, master, source-cache, evidence-ledger, or candidate store is mutated.

## CLI

```bash
python scripts/run_public_search_ranking_dry_run.py --all-examples --json
python scripts/validate_public_search_ranking_dry_run_report.py
python scripts/validate_public_search_ranking_dry_run_report.py --json
```

## Limitations

This is local synthetic dry-run behavior only. Manual external observations and ranking acceptance gates are still needed before any live/public ranking integration.

