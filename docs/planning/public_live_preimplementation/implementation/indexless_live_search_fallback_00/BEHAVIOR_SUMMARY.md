# Behavior Summary

## Local First

Search runs still call the existing local `SearchService` first.

If local reviewed results exist, fallback is not invoked and `fallback_summary` remains absent.

## Fallback Triggers

Fallback can attach when:

- local search returns no results
- local search is unavailable and fallback is configured

## Fallback States

Fallback output is recorded as one of:

- `candidate`
- `need`
- `policy_blocked`
- `unavailable`

Fallback output is never `verified`, reviewed truth, or a promoted record.

## Default Posture

Fallback is inert by default unless a provider and policy are injected. This preserves existing demo and local-index behavior.

## Projection

Gateway resolution-runs projection includes `fallback_summary` only when present. Gateway code does not receive a source provider and remains projection-only for this fallback path.
