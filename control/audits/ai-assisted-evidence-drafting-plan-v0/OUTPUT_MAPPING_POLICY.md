# Output Mapping Policy

Typed AI outputs can map only to candidates:

- `alias_candidate` -> contribution alias suggestion
- `metadata_claim_candidate` -> evidence metadata claim candidate
- `compatibility_claim_candidate` -> evidence or contribution compatibility
  candidate
- `review_claim_candidate` -> review-description observation candidate
- `member_path_candidate` -> member-path evidence candidate
- `source_match_candidate` -> source record or source observation candidate
- `identity_match_candidate` -> duplicate or identity candidate for review
- `explanation_draft` -> result explanation draft only
- `absence_explanation_draft` -> absence report candidate
- `contribution_draft_candidate` -> contribution item candidate

Every mapping requires typed output validation, provenance where possible, and
review. No mapping creates automatic acceptance.
