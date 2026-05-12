# R0-03B Execution Plan

ready: true
task size: two_shot_required
max expected changed files: 1707

## R0-03B-1

Create control/schemas target roots and move audit, fixture, preview, task, validator, deprecated, and generated scaffold schemas.

- moves: 378
- reference updates: 0

## R0-03B-2

Update references and validators that point at moved schemas.

- moves: 0
- reference updates: 1121

## R0-03B-3

Clean up product contract placement and compatibility aliases after control schemas move.

- moves: 208
- reference updates: 1121

