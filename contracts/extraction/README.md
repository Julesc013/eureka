# Extraction Contracts

Deep Extraction Contract v0 defines contract-only request, result summary, policy, and member-summary schemas for future metadata-first inspection of containers and nested records.

F-BUNDLE-01 adds fixture-only extraction sandbox contracts for Tier 0 outer metadata, Tier 1 member listing, and Tier 2 manifest-candidate extraction over tiny synthetic repo-local ZIP/TAR fixtures.

F-BUNDLE-02 adds fixture-only search integration contracts for reviewable search gaps, review seeds, WorkUnit seeds, and usefulness reports derived from explicit extraction results.

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
- `extraction_search_integration.v0.json`
- `extraction_search_gap.v0.json`
- `extraction_review_seed.v0.json`
- `extraction_workunit_seed.v0.json`
- `extraction_usefulness_report.v0.json`
- `container_descriptor.v0.json`
- `member_manifest.v0.json`
- `member_record.v0.json`
- `member_observation_candidate.v0.json`
- `extraction_risk_report.v0.json`
- `extraction_boundary_report.v0.json`
- `extraction_fixture_manifest.v0.json`
- `extraction_console_view.v0.json`

F0 adds a narrower, fixture-only and manifest-only foundation for member discovery. It defines policy, container descriptors, member manifests, member records, WorkUnit seed suggestions, risk reports, boundary reports, fixture manifests, and read-only console view models. F0 is not a production extraction runtime and does not enable arbitrary local files, live fetches, downloads, filesystem extraction, execution, evidence creation, reviewed records, or index mutation.
