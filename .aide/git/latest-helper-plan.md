# AIDE Git Helper Plan

- schema_version: aide.git-helper-plan.v0
- generated_by: aide-lite
- operation: plan
- status: blocked
- dry_run: true
- apply_requested: false
- push_requested: false
- non_mutating: true
- remote_mutation: false
- force_push_allowed: false

## Current State

- branch: dev
- role: integration
- commit: 21e4f766300d9b55498fca1b3edc1cace51b0776
- dirty_tree: true
- upstream: origin/dev
- policy_ready: true

## Planned Commands

- none

## Executed Commands

- none

## Blockers

- dirty_tree_requires_classification

## Warnings

- dirty_tree_detected

## Recommendations

- clean or classify the working tree before branch-sensitive helper actions

## Safety Boundary

Q29 helper plans are dry-run by default. Live AIDE branch creation, deletion,
merge, prune, promotion, push, and force-push are not performed by Q29
validation.
