# Local Review Queue Runtime

The Local Review Queue runtime records local review envelopes for candidates, source cache records, evidence candidates, bridge outputs, WorkUnit results, node policy evaluations, observation candidates, and related fixtures.

It is explicit-input only and local-only. It is not hosted moderation, evidence acceptance, candidate promotion, public truth acceptance, public index mutation, or master-index mutation.

## Review Entries

A review queue entry records:

- the review subject type and ref
- review status
- review decision
- required and missing evidence
- duplicate and conflict posture
- policy and rights/risk notes
- allowed and forbidden next actions
- review gates
- truth and product boundaries

The only current approval-like decision is `approve_for_promotion_dry_run`, which permits later dry-run planning only. It does not accept a record as public truth.

## Statuses, Subjects, And Decisions

Statuses include `queued`, `needs_review`, `request_more_evidence`, `duplicate_possible`, `conflict_detected`, `policy_blocked`, `rejected`, `deferred`, and `ready_for_promotion_dry_run`.

Subjects include candidate records, evidence candidates, source cache records, source-cache-to-evidence bridge results, WorkUnit results, node policy evaluations, SearchNeeds, observations, and future pack or connector review subjects.

Decisions include no decision yet, dry-run approval, source/search/workunit seed approval, more-evidence request, duplicate marker, conflict preservation, rejection, deferral, and policy/risk/rights blocks.

## Boundaries

The runtime does not call networks, APIs, models, providers, browsers, live sources, crawlers, scrapers, downloaders, uploaders, telemetry, hosted review systems, or account systems. It writes only when a script receives an explicit allowed output path.

Validation:

```bash
python scripts/validate_local_review_queue_runtime.py
python scripts/record_review_queue.py --input examples/review/queue_entries/candidate_needs_review_v0.json --check
python scripts/summarize_review_queue.py --input examples/review/queue_entries --check
```
