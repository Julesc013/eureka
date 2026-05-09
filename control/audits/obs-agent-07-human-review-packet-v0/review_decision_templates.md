# Review Decision Templates

Use one template per review item. Leave fields blank until a human reviewer makes a decision.

```json
{
  "review_item_id": "",
  "source_artifact_ref": "",
  "proposed_decision": "",
  "human_decision": null,
  "decision_rationale": "",
  "confidence": null,
  "approve_next_action": [],
  "reject_reason": "",
  "request_more_evidence_fields": [],
  "policy_notes": [],
  "source_policy_decision_required": false,
  "track_b_dependency": "",
  "do_not_treat_as_observed_baseline": true,
  "do_not_treat_as_evidence_truth": true,
  "do_not_mutate_master_index": true,
  "reviewer": null,
  "reviewed_at": null,
  "notes": []
}
```

Approving an item does not make it an observed baseline.
Approving an item does not make it accepted evidence truth.
Approving an item does not approve live source access.
Approving an item does not create runtime SearchNeeds.
Approving an item does not create executable WorkUnits.
Approving an item does not mutate the master index.
