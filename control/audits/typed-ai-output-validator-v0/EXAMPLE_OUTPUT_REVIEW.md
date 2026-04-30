# Example Output Review

The disabled stub provider now has four valid typed output examples:

- `alias_candidate.valid.json`
- `compatibility_claim_candidate.valid.json`
- `explanation_draft.valid.json`
- `metadata_claim_candidate.valid.json`

All examples are synthetic and hand-authored. They reference the disabled stub
provider, include required review, include prohibited uses, avoid private paths
and secrets, keep generated text short, and do not claim truth, rights
clearance, malware safety, or automatic acceptance.

Invalid cases are covered by tempfile-based tests rather than committed invalid
fixtures.
