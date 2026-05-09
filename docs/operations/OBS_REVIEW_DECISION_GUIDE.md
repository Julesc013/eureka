# OBS Review Decision Guide

## What This Guide Covers

This guide explains how a human reviewer should use the OBS review packet. It is for human review only. It does not authorize automation to approve, reject, run, crawl, scrape, download, execute, or publish anything.

## Review Packet Workflow

1. Read the grouped packet summary.
2. Review high-priority and blocked items first.
3. For each item, choose one decision option or leave it pending.
4. Record rationale and confidence.
5. Keep policy and Track B dependency notes attached to the decision.

Generated packets keep `human_decision`, `reviewer`, and `reviewed_at` blank. The reviewer fills those fields outside the generated artifact.

## Decision Meanings

`approve_as_source_lead_future` means the item may be used as a future source lead. It does not approve source access.

`approve_as_search_need_seed_future` means the item may be used as a future draft SearchNeed input. It does not create a runtime SearchNeed.

`approve_as_workunit_seed_future` means the item may be used as a future draft WorkUnit input. It does not create or execute a runtime WorkUnit.

`approve_for_manual_observation_future` means the item may be selected for human observation later. It does not mark the pending slot observed.

`request_more_evidence` means the item should not proceed until more local or human-reviewed evidence is available.

`mark_policy_blocked` means the item cannot proceed under current policy.

`mark_duplicate`, `defer`, `reject`, and `no_action` are governance decisions only.

## Source Policy Difference

A source lead is a clue. Source policy approval is a separate permission gate. A source-policy decision must happen before live source access, live probes, source sync, source connectors, scraping, crawling, downloads, accounts, or telemetry.

## Track B Dependency Difference

Track B contracts can make a future path legible, but contract presence is not runtime activation. SearchNeed seeds and WorkUnit seeds remain drafts until Track B defines and accepts the runtime path.

## More Evidence

Request more evidence when:

- the item depends on manual observation;
- local evidence is too weak;
- source policy is unclear;
- the item may duplicate another candidate;
- Track B runtime support is missing.

## No-Goals

- No automated review decisions.
- No source access approval.
- No runtime SearchNeed creation.
- No runtime WorkUnit creation or WorkUnit execution.
- No observed baseline creation.
- No accepted evidence truth.
- No public index or master-index mutation.

## Validation

Use:

```text
python scripts/validate_obs_human_review_packet.py
python scripts/summarize_obs_human_review_packet.py
```
