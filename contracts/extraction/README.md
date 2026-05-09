# Extraction Contracts

Deep Extraction Contract v0 defines contract-only request, result summary, policy, and member-summary schemas for future metadata-first inspection of containers and nested records.

F-BUNDLE-01 adds fixture-only extraction sandbox contracts for Tier 0 outer metadata, Tier 1 member listing, and Tier 2 manifest-candidate extraction over tiny synthetic repo-local ZIP/TAR fixtures.

This directory does not implement extraction runtime, archive unpacking, OCR, transcription, source fetching, payload execution, source-cache writes, evidence-ledger writes, candidate promotion, or index mutation.

Primary files:

- `deep_extraction_request.v0.json`
- `extraction_result_summary.v0.json`
- `extraction_policy.v0.json`
- `extraction_member.v0.json`
- `extraction_sandbox.v0.json`
- `extraction_target.v0.json`
- `extraction_result.v0.json`
- `extraction_manifest_candidate.v0.json`
- `extraction_candidate_effect.v0.json`
- `extraction_safety_report.v0.json`
