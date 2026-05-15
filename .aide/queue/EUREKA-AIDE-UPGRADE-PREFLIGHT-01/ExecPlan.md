# Q54 Exec Plan

## Scope

- Confirm this checkout is `julesc013/eureka`.
- Inspect git state, existing target AIDE Lite state, Eureka product boundaries, validators, source/evidence/index systems, and release bundle readiness.
- Write compact Q54 evidence and reports only.
- Generate the Q55 compact task packet if the existing target AIDE command supports it.

## Plan

1. Run the Git task-state guard and record any failures as preflight state.
2. Confirm repo identity from remote, top-level path, top-level files, and Eureka roots.
3. Inspect current `.aide/` state, queue entries, memory, golden tasks, policies, packets, reports, and target-local fixes.
4. Discover product roots, architecture checks, source/evidence/index contracts, validators, and reports.
5. Locate and validate the latest local AIDE release bundle read-only.
6. Run safe validation commands and record exact pass/warn/fail outcomes.
7. Write Q54 queue evidence and compact top-level reports.
8. Stage only Q54 artifacts and safe generated AIDE validation artifacts; commit only if safe.

## Boundary Crossing

Q54 crosses from AIDE metadata into product-source inspection only. It does not edit product roots, contracts, runtime, site, native, scripts, tests, or docs.

## Stop Condition

Stop at `needs_review`. Q55 must perform any upgrade in observe/compare/plan/dry-run mode before applying portable files.
