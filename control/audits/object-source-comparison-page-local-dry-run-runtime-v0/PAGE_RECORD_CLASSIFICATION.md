# Page Record Classification

The classifier is conservative and uses these dimensions:

- `page_kind`: `object_page`, `source_page`, `comparison_page`, `unknown`
- `page_status`: `synthetic_example`, `public_safe_example`, `fixture_backed`, `candidate`, `review_required`, `conflicted`, `placeholder`, `future`, `unknown`
- `lane`: `official`, `preservation`, `community`, `candidate`, `absence`, `conflicted`, `demo`, `unknown`
- `privacy_status`: `public_safe`, `redacted`, `local_private`, `rejected_sensitive`, `unknown`
- `public_safety_status`: `public_safe`, `review_required`, `rejected`, `unknown`
- `action_status`: `inspect_only`, `compare_only`, `cite_only`, `risky_actions_disabled`, `unsafe_action_claim_detected`, `unknown`
- `conflict_gap_status`: `no_known_conflict_or_gap`, `conflict_present`, `gap_present`, `conflict_and_gap_present`, `unknown`

Unsupported page kinds, unsafe actions, raw payload fields, URLs, private paths,
and secret-like fields make a record invalid. Unknown posture remains visible
and does not become a truth claim.
