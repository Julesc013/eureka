# Safe Driver Review Rules

These rules apply after the user returns hardware details.

## Review Boundaries

- Treat returned details as user-supplied evidence, not automatic truth.
- Match driver candidates to device identity, bus/interface, chipset, and exact
  Windows version.
- Prefer source-backed vendor, archive, manual, or checksum evidence.
- Preserve uncertainty when evidence conflicts.
- Keep generic vendor-family leads separate from exact driver recommendations.

## Required Before Recommendation

A specific driver recommendation requires:

- device identity match;
- Windows 98 variant compatibility evidence;
- source reference for the candidate driver;
- artifact identity evidence;
- safety and rights caveats;
- explicit review decision.

## Prohibited Without Stronger Evidence

- claiming compatibility is proven;
- claiming malware safety;
- claiming rights clearance;
- recommending execution or installation;
- treating an arbitrary mirror as trusted;
- treating a filename as exact artifact identity;
- promoting user memory or AI/model text into artifact truth.

## Allowed Outcomes

- `request_more_details`
- `review_candidate_driver_source`
- `mark_near_miss`
- `mark_blocked_for_user_details`
- `mark_need`
- `reject_candidate`

Do not create verified artifact claims from this packet alone.
