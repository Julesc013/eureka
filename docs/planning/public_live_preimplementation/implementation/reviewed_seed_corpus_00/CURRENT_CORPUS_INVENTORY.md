# Current Corpus Inventory

Task ID: `REVIEWED-SEED-CORPUS-00`

## Summary

The live repo has useful candidate, need, bounded absence, limited reviewed
metadata, and eval fixture material, but the six hard-query seed records created
for this task are not reviewed truth.

## Inventory

| Path | Current material | Truth posture | Reuse |
|---|---|---|---|
| `evals/hard_queries/hard_query_set_v0.json` | Six hard public-alpha pressure queries | Eval pressure only | Source of required query IDs and texts |
| `evals/hard_queries/fixtures_v0.py` | Synthetic candidate/need/near_miss/policy_blocked/unavailable fixtures | Not evidence, not reviewed truth | Shape reference for seed projection |
| `evals/hard_queries/seed_corpus/seed_corpus.v0.json` | Six seed items mapped to hard queries | Non-truth seed material | Current task output |
| `examples/review_batch/apply_next/limited_reviewed_metadata_records.json` | Limited reviewed metadata leads | Review-backed metadata only; `accepted_truth=false` | Support reference for one Windows 7 candidate |
| `examples/review_batch/apply_next/reviewed_known_needs.json` | Reviewed known needs | Reviewed need state, not object truth | Pattern for future reviewed needs |
| `examples/review_batch/apply_next/reviewed_bounded_absences.json` | Reviewed bounded absences | Bounded absence only, not global absence | Pattern for future reviewed absences |
| `examples/seed_batches/**/candidate_summaries.json` | Candidate seed batches | Candidate only; review required | Candidate backlog input |
| `examples/candidates/*.json` | Individual candidate examples | Candidate only; review required | Candidate format reference |
| `runtime/candidate_store/**` | Candidate persistence seam | Runtime seam, not corpus material by itself | Future implementation/review path |
| `runtime/search/need/**` | Search need seam | Runtime seam, not corpus material by itself | Future implementation/review path |
| `runtime/source/observation/**` | Source observation seam | Observation support, not truth | Future source-observation input |

## Seed Counts

| State | Count |
|---|---:|
| reviewed | 0 |
| candidate | 2 |
| need | 1 |
| near_miss | 1 |
| policy_blocked | 1 |
| unavailable | 1 |
| unknown | 0 |

## Alpha Gap

The current public-alpha benchmark is 50 hard queries, 200 reviewed records, and
500 candidate/need/near_miss/bounded-absence items. This task maps 6 hard
queries and creates 6 non-reviewed useful seed items.
