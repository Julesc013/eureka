# Candidate Promotion Policy v0

Candidate Promotion Policy v0 defines recommendation-only promotion assessments for provisional candidate records. Promotion policy is not promotion runtime, and candidate promotion runtime is not implemented.

A promotion assessment is not master-index mutation. It cannot accept a candidate as truth, update the candidate index, update source cache or evidence ledger state, update public search ranking, or write the master index.

## Gates

Promotion toward any future authoritative path requires structure, candidate type, source policy, provenance, evidence, privacy, rights, risk, conflict, duplicate, human, policy, and operator gates. AI output, probe output, pack output, and manual observation are not automatic truth.

## Evidence And Provenance

Evidence sufficiency is for future review eligibility only. Candidate-only evidence and AI-only output are insufficient for master-index promotion. Provenance must reference source, pack, validator, or review context before a future review queue can consider it.

## Privacy Rights And Risk

Raw query retention defaults to none. Promotion assessments must not contain private paths, secrets, account identifiers, IP addresses, unsafe private URLs, or unreviewed local result identifiers. Rights clearance and malware safety are not claimed by this policy.

## Decisions

Recommended decisions are recommendation-only: no_action, reject_candidate, quarantine_candidate, request_more_evidence, request_source_policy_review, request_rights_risk_review, mark_duplicate_candidate, supersede_candidate_future, eligible_for_review_queue_future, eligible_for_promotion_future, and not_eligible. Automatic promotion is forbidden.

## Boundaries

Candidate confidence is not truth. Destructive merge is forbidden. Future outputs such as review queue entries, evidence pack candidates, source cache candidates, evidence ledger candidates, rejection records, quarantine records, and master index candidates are not emitted in P65.

## Relations

This policy consumes Candidate Index v0 references and stays downstream of query observations, shared result cache entries, miss ledger entries, search needs, and probe queue items. It is upstream of future known absence pages, privacy/poisoning guard, demand dashboard, source sync worker, source cache/evidence ledger, and master index review queue work.
