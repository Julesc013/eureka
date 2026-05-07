# EUREKA-CTRL-01 Control Standards

## What Was Added

- Eureka-local structured commit and changelog policy.
- WorkUnit recovery and idempotency policy.
- Documentation quality and anti-bloat policy.
- Source-comment and docstring policy.
- A stdlib validator and changelog preview tool.
- Sample commit messages and WorkUnit examples.

## Why This Was Inserted Before Continuing Track A

Track A is now producing many contracts, audits, validators, and follow-up
tasks. The repo needs changelog-ready commits, repeatable WorkUnits, compact
documentation, and why-first source explanations before more generator or
runtime-adjacent work continues.

## Commit And Changelog Discipline

Future substantive commits should use Conventional Commit subjects, the required
Markdown sections including `## Why`, parseable changelog groups, and AIDE
trailers. `PASS_WITH_WARNINGS` is allowed when warnings are documented and there
are zero errors.

## WorkUnit Recovery

Repeated, duplicate, out-of-order, or partial prompts should be classified from
repo evidence. Complete tasks become validated noops, partial tasks resume from
missing acceptance criteria, and conflicting tasks are quarantined before work
continues.

## Documentation Quality

Docs should be accurate, compact, source-grounded, explicit about validation and
no-goals, and free of stale product claims. Link to canonical docs instead of
copying broad history into every audit.

## Source-Comment Policy

Comments should explain why, invariants, side effects, risk, recovery behavior,
and failure modes. The density bands are advisory only; existing code is not
hard-failed.

## Deferred

- Automatic changelog generation remains future work.
- Existing commit history is not rewritten.
- Existing source files are not comment-density audited as a hard gate.

## Validation Commands

- `git diff --check`
- `python -m json.tool control/audits/eureka-ctrl-01-control-standards-v0/eureka_ctrl_01_report.json`
- `python scripts/validate_eureka_control_policy.py`
- `python scripts/preview_eureka_changelog.py --message-file examples/commit_messages/valid_structured_commit.txt`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/validate_track_a_contracts.py`
- AIDE Lite `doctor`, `validate`, `test`, `selftest`, `verify`, `eval list`,
  `eval run`, `review-pack`, and `adapter validate`

## No-Goals

This task does not change Eureka product behavior, public routes, runtime,
generated site artifacts, hosting, live probes, source connectors, native
projects, pack import, review runtime, node runtime, downloads, uploads,
accounts, telemetry, master-index state, or public search semantics.

## Next Task

`TRACK-A-13 - Static SearchPage projection dry-run generator`
