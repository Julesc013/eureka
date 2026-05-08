# Observation Candidate Review

Observation candidates are reviewed planning records, not observations. Approval of an observation candidate does not equal observed external baseline evidence. Approval only decides what downstream safe action may happen next.

## Review States

- proposed
- needs_human_review
- approved_for_manual_observation
- approved_as_source_lead
- approved_as_work_unit_seed
- rejected
- duplicate
- policy_blocked
- needs_more_evidence
- deferred

## Review Actions

- approve
- reject
- request_more_evidence
- mark_duplicate
- mark_policy_blocked
- convert_to_search_need_seed
- convert_to_work_unit_seed
- convert_to_source_lead
- leave_manual_only

## Decision Boundary

Review decisions may approve a candidate as a source lead, a WorkUnit seed, or a manual-observation target. They must not mark it observed, turn agent text into evidence truth, approve master-index mutation, bypass source policy, or imply live source access.

Reviewers should record rationale, rejected next actions, policy notes, limitations, and follow-up required before any candidate enters downstream work.
