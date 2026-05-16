# EUREKA-AIDE-SYNC-01 ExecPlan

## Objective

Sync Eureka's AIDE Lite governance from the canonical Q31 AIDE Lite Pack
without importing AIDE source-repo state or changing Eureka product behavior.

## Scope

- Review the Q31 source pack and its manifest/checksum/provenance posture.
- Dry-run import into Eureka and record planned writes, conflicts, skips, and
  source-state exclusions.
- Target-sync portable governance files only:
  commit discipline, WorkUnit recovery, generic Git workflow policy, dry-run
  helper policy, golden tasks, tests, and target-safe docs/templates.
- Preserve Eureka memory, queue/evidence, generated context, target-local
  golden tasks, product source, and manual `AGENTS.md` content.
- Regenerate Eureka-local changelog, Git workflow/helper, task, review, ledger,
  and eval outputs after sync.

## Non-Goals

- No Eureka runtime/backend/site/connector/native/product changes.
- No branch creation, merge, push, prune, or helper `--apply`.
- No provider/model/network/GitHub API calls.
- No hook installation into `.git/hooks`.
- No Dominium or AIDE source repo mutation.

## Plan

1. Record baseline Git, AIDE Lite, source-pack, import dry-run, and architecture
   check results.
2. Commit the Q32 queue packet.
3. Apply targeted governance sync from the Q31 pack while preserving
   target-specific conflicts.
4. Run AIDE Lite validation and repair sync-only incompatibilities.
5. Regenerate target-local reports and packets.
6. Write final evidence, update compact docs, set status to `needs_review`, and
   commit the result.

## Validation Intent

- AIDE Lite doctor/validate/test/selftest/eval/verify/review-pack.
- Commit checker, commit template, changelog preview.
- Task inspect/status/noop-check.
- Git detect/doctor/status/policy/plan and dry-run helpers.
- Architecture boundary check.
- Targeted secret scan.

## Review Gate

This task ends at `needs_review`; it does not approve product work or target
branch mutation.
