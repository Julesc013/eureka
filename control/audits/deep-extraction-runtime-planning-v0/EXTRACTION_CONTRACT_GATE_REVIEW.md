# Extraction Contract Gate Review

Contract status:

- Request schema: `contracts/extraction/deep_extraction_request.v0.json` present.
- Result summary schema: `contracts/extraction/extraction_result_summary.v0.json` present.
- Policy schema: `contracts/extraction/extraction_policy.v0.json` present.
- Member schema: `contracts/extraction/extraction_member.v0.json` present.
- Validator: `scripts/validate_deep_extraction_contract.py` present.
- Request validator: `scripts/validate_deep_extraction_request.py` present.
- Result summary validator: `scripts/validate_extraction_result_summary.py` present.
- Stdout-only dry-run request helper: `scripts/dry_run_deep_extraction_request.py` present.
- Example roots: seven synthetic public-safe examples under `examples/extraction`.

The contract includes tier taxonomy, no-runtime/no-mutation booleans, and
metadata-first examples. It does not approve runtime extraction.

Gaps:

- Contract policy is not runtime sandbox approval.
- Concrete operator-approved resource limit values are incomplete.
- Future runtime request policy must still reject public/request-selected paths.

