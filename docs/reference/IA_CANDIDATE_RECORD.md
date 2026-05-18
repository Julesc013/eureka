# IA Candidate Record

IA candidate records are provisional search/discovery records derived from IA
evidence candidates.

Required fields include:

- `candidate_id`
- `candidate_kind`
- `source_id`
- `source_cache_record_ids`
- `evidence_ids`
- `observation_ids`
- `candidate_subject`
- `candidate_title`
- `candidate_summary`
- `source_locator`
- `item_identifier`
- `mediatype`
- `collection_refs`
- `file_summary`
- `checksum_summary`
- `claim_summary`
- `provenance`
- `support_level`
- `confidence`
- `uncertainty`
- `limitations`
- `risk_flags`
- `rights_flags`
- `review_required`
- `accepted_truth`
- `reviewer_decision`

Allowed candidate kinds are:

- `ia_item_candidate`
- `ia_media_metadata_candidate`
- `ia_file_list_candidate`
- `ia_collection_member_candidate`
- `ia_source_locator_candidate`
- `ia_near_miss_candidate`
- `ia_absence_or_missing_item_candidate`

Required invariants:

- `review_required` is true
- `accepted_truth` is false
- `reviewer_decision` is pending or null
- `reviewed_record_created` is false
- reviewed and master index mutation flags are false
- `raw_response_committed` is false
- `download_performed` is false

Candidate records retain source-cache and evidence provenance so future review
can trace every provisional candidate back to the source observation path.
