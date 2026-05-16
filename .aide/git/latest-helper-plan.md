# AIDE Git Helper Plan

- schema_version: aide.git-helper-plan.v0
- generated_by: aide-lite
- operation: plan
- status: ready_dry_run
- dry_run: true
- apply_requested: false
- push_requested: false
- non_mutating: true
- remote_mutation: false
- force_push_allowed: false

## Current State

- branch: dev
- role: integration
- commit: 2af3514dd8fbf3a2e11661d07f12641ffab99796
- dirty_tree: false
- upstream: origin/dev
- policy_ready: true

## Planned Commands

- none

## Executed Commands

- none

## Blockers

- none

## Warnings

- none

## Recommendations

- run git promote --dry-run --from dev --to main after review gates

## Safety Boundary

Q29 helper plans are dry-run by default. Live AIDE branch creation, deletion,
merge, prune, promotion, push, and force-push are not performed by Q29
validation.
