# Source Cache To Evidence Bridge Model

The bridge sits between the fixture-only local source cache runtime and the fixture-only local evidence ledger runtime.

Source cache records are observations about sources. Evidence ledger records are reviewable claim candidates. The bridge translates the former into the latter, preserving provenance, limitations, review gates, truth boundaries, and product boundaries.

## Result Shape

A bridge result contains:

- `bridge_result_id`
- `bridge_status`
- `source_cache_record_ref`
- `generated_evidence_candidates`
- `mapping_results`
- `provenance_summary`
- `source_locator_summary`
- `limitations`
- `warnings`
- `review_gates`
- `truth_boundary`
- `product_boundary`

Each mapping result states the input field, output evidence type, output claim type, provenance status, review requirement, and false acceptance/master-index flags.

## Evidence Candidate Shape

Generated candidates use the local evidence ledger record shape from the B-16 runtime. The bridge currently produces metadata, source-observation, identity, or review-status candidates. It does not create persistent append storage and does not bypass evidence-ledger validation.

## Review And Provenance

Every candidate links back to the source cache record through `lineage_refs` and `related_source_cache_refs_future`. Missing source locator or provenance context is reported as a warning and keeps the result review-bound.

## No-Goals

The bridge does not fetch sources, run connectors, perform observations, accept claims, merge conflicts, create a public record, write private local state, or mutate the master index.
