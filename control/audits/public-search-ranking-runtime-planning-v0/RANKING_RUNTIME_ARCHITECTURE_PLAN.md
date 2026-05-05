# Ranking Runtime Architecture Plan

Future modules only:

- `runtime/engine/ranking/factors.py`: future factor extraction from result envelopes.
- `runtime/engine/ranking/evidence_weighted.py`: future evidence-weighted scorer.
- `runtime/engine/ranking/compatibility.py`: future compatibility-aware scorer.
- `runtime/engine/ranking/merge_features.py`: future grouping/identity features.
- `runtime/engine/ranking/explain.py`: future explanation adapter.
- `runtime/engine/ranking/policy.py`: future no-hidden-score/no-telemetry guard.
- `runtime/engine/ranking/regression.py`: future ranking regression harness.
- `runtime/engine/ranking/errors.py`: future stable error model.
- `runtime/gateway/public_api/ranking.py`: future public-search adapter.

P97 creates none of those runtime files.

Future dependencies: public index reader, result envelope, evidence-weighted ranking contract, compatibility-aware ranking contract, result merge/deduplication contract, identity resolution contract, search result explanation contract, search usefulness evals, regression corpus, and operator kill switch.

Required future env flags: `EUREKA_PUBLIC_SEARCH_RANKING_ENABLED=0`, `EUREKA_PUBLIC_SEARCH_RANKING_MODE=current_order`, `EUREKA_PUBLIC_SEARCH_RANKING_DRY_RUN=1`, `EUREKA_PUBLIC_SEARCH_RANKING_EXPLAIN=0`, `EUREKA_PUBLIC_SEARCH_RANKING_HIDDEN_SCORE=0`, `EUREKA_PUBLIC_SEARCH_RANKING_SUPPRESS_RESULTS=0`, `EUREKA_PUBLIC_SEARCH_RANKING_TELEMETRY=0`, `EUREKA_PUBLIC_SEARCH_RANKING_USER_PROFILE=0`, `EUREKA_PUBLIC_SEARCH_RANKING_AD_SIGNAL=0`, `EUREKA_PUBLIC_SEARCH_RANKING_MODEL_CALLS=0`, `EUREKA_PUBLIC_SEARCH_RANKING_LIVE_SOURCE_CALLS=0`.
