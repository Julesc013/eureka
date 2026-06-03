# Review Ledger Spec

## Purpose

Review is the operational truth boundary.

## Review Decisions

- `promote`
- `reject`
- `supersede`
- `mark_near_miss`
- `mark_need`
- `mark_policy_blocked`
- `request_more_evidence`

## Required Inputs

Every review event must cite evidence, source observation, absence, or rationale
and must identify actor, timestamp, decision, target, resulting status, public
visibility posture, and rollback/supersession relationship where relevant.

## Existing Paths To Audit

- `contracts/stores/review_event.v0.json`
- `contracts/review/**`
- `runtime/review/**`
- `runtime/local/review/**`

## Gate

Every reviewed record has a review event. No candidate, SourceObservation,
synthetic fixture, or AI output self-promotes.

