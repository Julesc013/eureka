# Track B Runtime Spine Summary

Track B now supports a local, replayable, review-gated lifecycle:

| Stage | Input | Output | Boundary |
| --- | --- | --- | --- |
| QueryObservation | Explicit query fixture | Local query signal | Not public telemetry |
| SearchMiss | Query signal | Local miss record | Not public search behavior |
| SearchNeed | Miss record | Reviewable SearchNeed | Not accepted need truth |
| WorkUnit | SearchNeed or review item | Governed task record | Not executed here |
| WorkUnitResult | Dry-run WorkUnit | Local dry-run result | Not external observation |
| NodePolicyEvaluation | Node policy plus requested action | Local evaluation report | No source approval by default |
| Candidate | WorkUnit result or need | Provisional candidate | Not accepted public truth |
| SourceCache | Explicit fixture | Local observation record | Not accepted evidence |
| EvidenceLedger | Fixture, pack, or bridge candidate | Evidence candidate | Not evidence truth |
| SourceCacheToEvidenceBridge | Source cache record | Evidence candidate | No truth conversion |
| ReviewQueue | Candidate/evidence/source/bridge item | Local review envelope | Not hosted moderation |
| CandidatePromotionDryRun | Candidate plus review/evidence refs | Readiness report | Not promotion |
| ReviewedPublicIndexRebuildContract | Reviewed local records | Future proposal contract | No public index mutation |
| PackBuilder | Local records | Pack draft | Not imported/submitted |
| PackExport | Pack draft | Export draft with fixity | Not signed, uploaded, or accepted |

No stage currently enables live source access, connector execution, external
API calls, provider calls, public-index mutation, master-index mutation, or
accepted truth creation.
