# Explanation Runtime Architecture Plan

Future modules only:

- `runtime/engine/explanations/input.py`: result-envelope validator.
- `runtime/engine/explanations/components.py`: component assembler.
- `runtime/engine/explanations/match.py`: match/recall explanation builder.
- `runtime/engine/explanations/sources.py`: source coverage explanation builder.
- `runtime/engine/explanations/evidence.py`: evidence/provenance builder.
- `runtime/engine/explanations/identity.py`: grouping/identity builder.
- `runtime/engine/explanations/ranking.py`: ranking explanation adapter.
- `runtime/engine/explanations/compatibility.py`: compatibility builder.
- `runtime/engine/explanations/gaps.py`: absence/near-miss/gap builder.
- `runtime/engine/explanations/actions.py`: action-safety builder.
- `runtime/engine/explanations/copy.py`: user-facing copy renderer.
- `runtime/engine/explanations/policy.py`: privacy, no-model, no-hidden-score
  guard.
- `runtime/engine/explanations/report.py`: dry-run report builder.
- `runtime/engine/explanations/errors.py`: bounded error model.
- `runtime/gateway/public_api/explanations.py`: future disabled API adapter.

Required future flags:

- `EUREKA_SEARCH_EXPLANATION_RUNTIME_ENABLED=0`
- `EUREKA_SEARCH_EXPLANATION_DRY_RUN=1`
- `EUREKA_SEARCH_EXPLANATION_PUBLIC_RESPONSE=0`
- `EUREKA_SEARCH_EXPLANATION_API_ROUTES=0`
- `EUREKA_SEARCH_EXPLANATION_MODEL_CALLS=0`
- `EUREKA_SEARCH_EXPLANATION_AI_ANSWERS=0`
- `EUREKA_SEARCH_EXPLANATION_HIDDEN_SCORES=0`
- `EUREKA_SEARCH_EXPLANATION_SUPPRESS_RESULTS=0`
- `EUREKA_SEARCH_EXPLANATION_TELEMETRY=0`
- `EUREKA_SEARCH_EXPLANATION_SOURCE_CACHE_READS=0`
- `EUREKA_SEARCH_EXPLANATION_EVIDENCE_LEDGER_READS=0`
- `EUREKA_SEARCH_EXPLANATION_MUTATE_ANYTHING=0`

P106 creates no runtime files for these modules.

