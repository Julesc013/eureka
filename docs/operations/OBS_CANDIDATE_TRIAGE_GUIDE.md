# OBS Candidate Triage Guide

This guide explains how OBS side-lane ObservationCandidate records are ordered for human review.

Triage is advisory. It is not approval, not source access approval, not evidence truth, and not public truth.

## Priority Bands

- `high`: strong repo-local evidence and clear review value.
- `medium`: useful candidate with more uncertainty, narrower scope, or higher review cost.
- `low`: lower-priority candidate or broad policy question.
- `blocked`: policy-blocked until a human/operator decision changes the posture.
- `insufficient_local_evidence`: too little committed local evidence to infer detail.

## Factors

Triage considers source family fit, old-platform relevance, hidden member discovery relevance, metadata likelihood, failure mode relevance, source policy risk, rights or malware risk, manual review cost, downstream Track B readiness, and local evidence strength.

These factors only order review work. They do not change candidate state.

## Recommended Actions

Recommended actions are future-only:

- `approve_as_source_lead_future`
- `approve_as_workunit_seed_future`
- `approve_as_search_need_seed_future`
- `approve_for_manual_observation_future`
- `reject_future`
- `mark_duplicate_future`
- `mark_policy_blocked_future`
- `request_more_evidence_future`
- `defer_future`

The suffix is deliberate. OBS-AGENT-03 does not approve, reject, promote, merge, deduplicate, or convert candidates.

## Human Review Meaning

A later human review may decide the next safe action. That decision still does not make a candidate observed baseline evidence, accepted evidence truth, or public truth. It also does not mutate the master index.

Approving a source lead does not approve live source access. Approving a WorkUnit or SearchNeed seed does not create the WorkUnit or SearchNeed record until future Track B contracts and review gates are ready.

## Parallel Track B

The review queue can progress in parallel with Track B because queue entries are governance records. Track B should consume them only when matching contracts exist and after review decisions are recorded.

## No-Goals

- No live source access.
- No external search, API call, browser, scraping, or crawling.
- No source sync, connector runtime, download, install, upload, account, or telemetry.
- No rights-clearance, malware-safety, installability, or exhaustive-search claim.
- No observed baseline, accepted evidence, SearchNeed, WorkUnit, or master-index mutation.
