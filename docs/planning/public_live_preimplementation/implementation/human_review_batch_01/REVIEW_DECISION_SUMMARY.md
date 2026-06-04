# Review Decision Summary

Review actor:

```text
actor_id: human_review_batch_01_operator
actor_type: operator_assisted_review
review_mode: local_record_review
```

Summary by decision:

| Decision | Count | Result |
|---|---:|---|
| `promote` | 1 | New reviewed seed record for 7-Zip Windows 7 support |
| `supersede` | 3 | Duplicate Firefox facts linked to existing reviewed seed records |
| `mark_near_miss` | 3 | FlashFXP, Sound Blaster 16 manual, RADIANCE |
| `mark_need` | 1 | Windows 98 driver hardware-detail blocker |
| `request_more_evidence` | 4 | SmartFTP, Core FTP, CT1740 manual, Byte ray-tracing article lead |

All decisions have review events. Only the promote decision creates reviewed truth.
