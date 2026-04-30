# Static Artifact Promotion Review v0

This audit pack records the local promotion review for Eureka's generated
static publication artifact.

Decision: `conditionally_promoted_pending_github_actions_evidence`.

The review finds `site/dist/` valid as the active repo-local static artifact
and as the artifact configured for the GitHub Pages workflow. The review does
not claim that GitHub Pages has deployed successfully, because no GitHub
Actions run evidence is recorded in this pack.

This milestone adds no public search runtime, API route, backend hosting, live
probe, crawler, relay runtime, native client, download surface, account system,
telemetry, signing key, or production-readiness claim.

## Files

- `CURRENT_STATIC_ARTIFACT.md`: current artifact path and repo shape.
- `PROMOTION_DECISION.md`: promotion decision and evidence boundary.
- `VALIDATION_EVIDENCE.md`: local command evidence for the review.
- `WORKFLOW_REVIEW.md`: GitHub Pages workflow review.
- `GENERATED_ARTIFACT_REVIEW.md`: generated artifact ownership review.
- `STATIC_SAFETY_REVIEW.md`: static safety and no-JS review.
- `BASE_PATH_REVIEW.md`: base-path and link portability review.
- `PUBLIC_DATA_SURFACE_REVIEW.md`: public data and static surface review.
- `STALE_REFERENCE_REVIEW.md`: stale-name classification.
- `RISK_REGISTER.md`: remaining risks.
- `BLOCKERS_AND_DEFERRED_WORK.md`: blockers and deferred work.
- `NEXT_STEPS.md`: next milestone sequence.
- `static_artifact_promotion_report.json`: structured report for validation.
