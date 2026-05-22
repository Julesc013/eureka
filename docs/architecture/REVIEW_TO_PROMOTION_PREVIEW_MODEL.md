# Review To Promotion Preview Model

Review is the boundary between candidate material and reviewed local projection. A candidate can become a review item, but it remains candidate-only until an operator-gated decision is recorded.

## Decisions

Supported decisions are `accept_local_reviewed`, `reject_wrong_object`, `reject_wrong_version`, `reject_wrong_platform`, `needs_more_evidence`, `duplicate`, `unsafe`, `rights_risk`, and `defer`.

Only `accept_local_reviewed` can create a promotion preview. Rejections, duplicates, unsafe items, rights risks, and deferrals keep the item out of the reviewed local projection.

## Preview Semantics

A promotion preview contains:

- a reviewed local record preview
- evidence and source summaries
- limitations
- action posture
- blocked actions
- an index delta preview

The preview does not write to the reviewed index. It is an operator review artifact that explains what would happen if a later explicit refresh path is allowed.
