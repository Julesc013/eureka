# WorkUnit Seed Review Packet

## Top Review Items

1. `workunit_seed_source_policy_review_archive_metadata_v0`
   - Recommended action: `approve_as_workunit_seed_future`
   - Rationale: high-priority source policy review draft derived from OBS-03 and OBS-04 local metadata.
   - Policy status: source policy decision still required before any future source interaction.

2. `workunit_seed_metadata_probe_planning_archive_v0`
   - Recommended action: `approve_as_workunit_seed_future`
   - Rationale: high-priority metadata probe planning draft, but only after source policy review.
   - Policy status: future/deferred; no source interaction is allowed by this packet.

3. `workunit_seed_extraction_gap_driver_inf_v0`
   - Recommended action: `approve_as_workunit_seed_future`
   - Rationale: extraction/member-access planning from local eval and SearchNeed seed material.
   - Policy status: repo-local only; future extraction capability remains separate.

4. `workunit_seed_policy_blocked_broad_web_v0`
   - Recommended action: `mark_policy_blocked_future`
   - Rationale: useful-looking broad web work idea remains blocked by source policy.
   - Policy status: blocked until human/operator review.

## What Approval Would Mean

Approval in a future review packet would mean the seed may be used as an input
to later planning once matching Track B contracts and review gates exist.

## What Approval Would Not Mean

Approving a WorkUnit seed does not execute it.

Approving a WorkUnit seed does not make it an observed baseline.

Approving a WorkUnit seed does not make it accepted evidence.

Approving a WorkUnit seed does not create a runtime WorkUnit until Track B accepts it.

Approving a WorkUnit seed does not mutate the master index.

Approving a WorkUnit seed does not approve live source access.

## Human Review Needs

- Confirm each work label, input set, allowed action, and forbidden action.
- Decide whether a seed is duplicate, too broad, or missing evidence.
- Keep policy-blocked seeds blocked until source policy review changes that posture.
- Defer runtime activation until Track B WorkUnit runtime exists.
