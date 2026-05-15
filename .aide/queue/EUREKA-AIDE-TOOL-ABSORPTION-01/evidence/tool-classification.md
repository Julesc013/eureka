# Tool Classification

## Classification Outputs

- `.aide/tools/latest-tool-classification.json`
- `.aide/tools/latest-tool-classification.md`
- `.aide/tools/eureka-tool-classification.json`

## Fate Summary

- `keep`: 1
- `wrap`: 1878
- `unknown`: 285

`drop_candidate` is not deletion approval. Q56 did not classify Eureka source/evidence/index systems as junk and did not authorize any deletion.

## Risk Summary

Base AIDE risk classes:

- `low`: 306
- `medium`: 1156
- `release`: 439
- `destructive`: 8
- `security`: 1
- `unknown`: 254

Q56 Eureka risk tags add preservation-focused sensitivity for architecture, source mutation, evidence mutation, index mutation, network, release, build, and authority boundaries.

## Owner / Status Summary

The inventory includes:

- AIDE control-plane metadata and generated outputs under `.aide/**`.
- Eureka product validators and scripts under `scripts/**`.
- Test lanes under `tests/**`, `control/inventory/tests/command_matrix.json`, and `docs/operations/TEST_AND_EVAL_LANES.md`.
- Product contract/schema and runtime validation surfaces under `contracts/**` and `runtime/**`.
- Static site and snapshot validation/build surfaces under `site/**`, `scripts/**`, and `snapshots/**`.

## Unknowns

Unknown fate candidates: 285. These remain preserve/manual-review only. Q56 treats unknown as "do not execute, do not migrate, do not delete."

Representative unknown candidates from AIDE warnings:

- `.aide/hooks/commit-msg`
- `.aide/policies/export-import.yaml`
- `.aide/prompts/AIDE-SYNC-01.md`
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/import-review.md`
- `.aide/tools/*.schema.json`

## High-Risk Tools

High-risk categories include release-sensitive, destructive-candidate, security-sensitive, network-sensitive, source-mutation-sensitive, evidence-mutation-sensitive, index-mutation-sensitive, build-sensitive, and authority-sensitive paths. They remain preserve/wrap-plan only in Q56.

## No-Delete / No-Rename Statement

Q56 did not delete, rename, move, migrate, retire, archive, or rewrite any existing tool. All future wrapper, adaptation, migration, or retirement work requires a new reviewed queue phase with evidence.
