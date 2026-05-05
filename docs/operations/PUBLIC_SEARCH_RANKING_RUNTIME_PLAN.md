# Public Search Ranking Runtime Plan

Status: planning-only.

Purpose: plan a future bounded, explainable, evidence-weighted, compatibility-aware public search ranking runtime without implementing it.

Readiness decision: `ready_for_local_dry_run_runtime_after_operator_approval`. Hosted staging is blocked by unverified deployment evidence. Production quality claims are blocked by missing external baseline observations.

## Readiness Gates

Required before implementation: evidence-weighted ranking contract, compatibility-aware ranking contract, result merge/deduplication contract, identity resolution contract, search result explanation contract, public search contract, result-card contract, public search safety, public index contract, eval gates, deterministic tie-break, no-hidden-score policy, no telemetry/user-profile/ad/model signals, no suppression, fallback, hosted deployment evidence for hosted mode, and operator approval.

## Why Runtime Is Not Implemented Yet

P97 does not implement ranking runtime, change public search order, change public search responses, add hidden scores, suppress results, add telemetry, call models, add a ranking store, call live sources, or mutate source/evidence/candidate/public/local/master records.

Plain boundary: no runtime ranking, no public search order change, no hidden scores, no result suppression, no telemetry, and no mutation.

## Ranking Input And Output Model

Future inputs are the query envelope, public index result candidates, result card fields, source/evidence summaries, identity/grouping refs, compatibility hints, gap/absence fields, and action safety fields. Forbidden inputs include raw private query, IP address, account ID, session ID, telemetry profile, ad signals, user profile, live connector responses, arbitrary URLs, local paths, and private cache records.

Future outputs are the same result set, proposed rank order, ranking explanation refs, factor summaries, uncertainty/conflict/gap notices, no suppressed results, and stable fallback to current order.

## Future Ranking Pipeline

Validate request, read controlled result set, optionally attach grouping metadata, extract public-safe factors, compute evidence-weighted and compatibility-aware factors, attach conflict/gap/action-safety cautions, apply deterministic tie-break, reference explanations, and fall back to current order on failure.

## Integrations

Evidence-weighted integration uses evidence strength, provenance, source posture, freshness, conflicts, provisional status, gap transparency, action safety, and rights/risk caution without treating any factor as truth.

Compatibility-aware integration uses public-safe target profile and platform evidence while forbidding installability, dependency-safety, package-manager, emulator, or VM claims/actions.

Result merge and identity integration preserves alternatives, conflicts, and variants without destructive merge, duplicate deletion, or candidate promotion.

Search result explanation integration requires every ranked result to be explainable with match/source/evidence/ranking/grouping/compatibility/gap/action safety components.

## Eval And Regression Gates

Archive evals must stay satisfied, search usefulness must not regress without explanation, external baselines must be recorded before production-quality claims, ranking regression corpus is required, deterministic tie-break is required, and suppression must remain impossible.

## Safe Fallback And Rollback

Ranking is disabled by default. Current order fallback and kill switch are mandatory. If ranking or explanation fails, return current order. Hosted rollback returns to the previous search wrapper.

## Privacy And Security

No telemetry, raw query retention, hidden scores, user profiles, account/session/IP ranking, ad signals, secret model scoring, private paths/URLs, result suppression, local file access, live source calls, model calls, ranking-store writes, downloads, installs, execution, uploads, or accounts.

## Phases

Phase 0 keeps disabled and completes planning. Phase 1 local dry-run uses synthetic/public index fixtures only. Phase 2 shadow ranking returns current order and writes only test reports. Phase 3 local development visible ranking requires explanations. Phase 4 hosted staging remains disabled-by-default behind safety/eval gates. Phase 5 public alpha requires fallback and user-visible explanations.

## Next Steps

Next branch: P98 Source Cache Local Dry-Run Runtime v0 only after approval.
