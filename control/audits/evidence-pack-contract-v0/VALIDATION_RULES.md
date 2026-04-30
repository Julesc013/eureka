# Validation Rules

`scripts/validate_evidence_pack.py` validates:

- manifest fields and lifecycle status
- required files and docs
- `CHECKSUMS.SHA256`
- JSONL parsing
- evidence id uniqueness
- allowed evidence kinds and claim types
- source reference shape and locator kind
- privacy/status consistency
- 500-character snippet limit
- prohibited credential/private-key fields
- private local path rejection
- executable payload extension rejection
- no import/index/upload/network behavior in manifest flags

The validator does not import, index, upload, execute, fetch, or scrape.
