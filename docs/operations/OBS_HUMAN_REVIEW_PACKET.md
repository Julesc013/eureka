# OBS Human Review Packet

## Purpose

The OBS human review packet is a compact decision aid for the user. It collects OBS candidates, SearchNeed seed drafts, WorkUnit seed drafts, source-policy decision previews, and OBS/Track B synchronization items into one review surface.

It does not make decisions. All generated real review items keep `human_decision` blank.

## How To Read It

Each review item shows:

- the source artifact and identifier;
- a short summary;
- the recommended decision option;
- policy status;
- Track B dependency;
- blank human decision fields.

Use the packet to approve future conversion work, request more evidence, mark items duplicate, mark items policy-blocked, defer, reject, or take no action.

## Decision Options

- `approve_as_source_lead_future`: the item may become a source lead for future review work.
- `approve_as_search_need_seed_future`: the item may become a future SearchNeed seed input.
- `approve_as_workunit_seed_future`: the item may become a future WorkUnit seed input.
- `approve_for_manual_observation_future`: the item may be selected for future human manual observation.
- `request_more_evidence`: the item needs stronger repo-local or human-reviewed evidence before conversion.
- `mark_duplicate`: the item appears to overlap another item.
- `mark_policy_blocked`: the item remains blocked by source or product policy.
- `defer`: the item is useful but not ready.
- `reject`: the item should not proceed.
- `no_action`: the item is informational only.

## What Approval Does Not Mean

Approving an item does not make it an observed baseline. Approving an item does not make it accepted evidence truth. Approving an item does not approve live source access. Approving an item does not create runtime SearchNeeds. Approving an item does not create executable WorkUnits. Approving an item does not mutate the master index.

## Source Policy

Source-policy decisions are separate from source leads. A useful source lead may still remain blocked. Any live source access, source connector, source sync, or live probe requires a separate source policy approval path.

## SearchNeed Seeds

SearchNeed seed approval means the seed may be considered for future Track B conversion. It does not create a runtime SearchNeed.

## WorkUnit Seeds

WorkUnit seed approval means the seed may be considered for future Track B conversion. It does not create an executable WorkUnit and does not execute work.

## Track B Dependencies

Track B defines runtime structure and execution. OBS review can prepare future inputs, but Track B must accept them through governed contracts and runtime gates before anything can run or affect public truth.

## Requesting More Evidence

Use `request_more_evidence` when local evidence is ambiguous, policy state is unclear, or a candidate needs human manual observation before conversion.

## Policy-Blocked Items

Use `mark_policy_blocked` when the item cannot proceed without explicit source policy, rights, safety, or runtime approval. The item remains useful as a planning note but cannot drive live access.

## Validation

Use:

```text
python scripts/build_obs_human_review_packet.py --list-inputs
python scripts/build_obs_human_review_packet.py --check
python scripts/validate_obs_human_review_packet.py
python scripts/summarize_obs_human_review_packet.py
```

## No-Goals

- No actual human decisions by automation.
- No source approval.
- No external observation.
- No runtime SearchNeed creation.
- No runtime WorkUnit creation or WorkUnit execution.
- No accepted evidence truth.
- No observed baseline creation.
- No master-index mutation.
