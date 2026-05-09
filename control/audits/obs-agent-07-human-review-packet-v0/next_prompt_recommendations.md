# Next Prompt Recommendations

## Human Review Prompt

Use:

```text
HUMAN-OBS-REVIEW-01 - Review OBS candidate packet
```

Review `human_review_packet.md` and fill decisions outside the generated packet.

## Safe Review Order

1. High-priority source lead and archive metadata items.
2. Source policy blocked items.
3. SearchNeed seed drafts.
4. WorkUnit seed drafts.
5. Track B dependency notes.

## Do Not Ask The Next Agent To

- approve source access;
- run live probes;
- create runtime SearchNeeds;
- create or execute WorkUnits;
- mark pending observations as observed;
- create accepted evidence truth;
- mutate the master index.
