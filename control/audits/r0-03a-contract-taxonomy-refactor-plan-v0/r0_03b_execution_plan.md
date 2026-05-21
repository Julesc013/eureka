# R0-03B Execution Plan

ready: true
task size: two_shot_required
max expected changed files: 1270

## R0-03B-1

Create control/schemas target roots and move audit, fixture, preview, task, validator, deprecated, and generated scaffold schemas.

- moves: 21
- reference updates: 0

## R0-03B-2

Update references and validators that point at moved schemas.

- moves: 0
- reference updates: 1017

## R0-03B-3

Clean up product contract placement and compatibility aliases after control schemas move.

- moves: 232
- reference updates: 1017

