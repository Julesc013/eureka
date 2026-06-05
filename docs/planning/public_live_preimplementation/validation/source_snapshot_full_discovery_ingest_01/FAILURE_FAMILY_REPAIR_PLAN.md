# Failure Family Repair Plan

## Priority

1. `architecture_boundary_drift`
2. `generated_artifact_drift`
3. `source_snapshot_baseline_drift`
4. `queue_handoff_drift`
5. `contract_schema_drift`

This order follows the ingest prompt priority while recognizing that
`queue_handoff_drift` is the largest family by count.

## Repair Families

### `architecture_boundary_drift`

Recommended task:

```text
ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01
```

Representative evidence:

- `runtime/source/observation/internet_archive_live_transport.py` is reported by the R0 legacy leakage validator.
- `contracts/publication/public_alpha_ux_mvp_reassess.v0.json` is reported by the runtime architecture leakage validator for production-looking task/control vocabulary.
- Strict repo-structure validation reports unresolved `scripts` debt.

Risk:

Medium. Repair must distinguish real boundary violations from stale validator
allowlists. Do not move directories broadly and do not add new top-level roots.

### `generated_artifact_drift`

Recommended task:

```text
GENERATED-ARTIFACT-DRIFT-REPAIR-01
```

Representative evidence:

- Validator output refuses forbidden output roots such as `site/dist`,
  `runtime`, and `contracts`.

Risk:

Medium. Do not hand-edit generated artifacts or checksums. Use repo generators
or update validators only when repo policy says the validator is stale.

### `source_snapshot_baseline_drift`

Recommended task:

```text
SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01
```

Representative evidence:

- Local worker and source observation validation are grouped in the same family
  with a failing status.

Risk:

Medium. Keep source observation semantics non-truth-making. Do not add live
source calls, downloads, or Wayback replay.

### `queue_handoff_drift`

Recommended task:

```text
QUEUE-HANDOFF-DRIFT-REPAIR-01
```

Representative evidence:

- HUNT and LOCAL validators expect old queue successors.
- Promotion validators expect older `dev`/`main` alignment assumptions.
- Latest task packet remains stale for the current public-live sequence.

Risk:

Medium. Queue state must not be mutated blindly. Repair should reconcile stale
operation validators, repo-health docs, and queue/task-packet expectations
against current authority.

### `contract_schema_drift`

Recommended task:

```text
CONTRACT-SCHEMA-DRIFT-REPAIR-01
```

Representative evidence:

- TSIS validator CLI returns non-zero.

Risk:

Low to medium. Repair should be a narrow validator/contract alignment task, not
a broad TSIS expansion.

## Rerun Requirement

After each repair family, run focused validators first. Run external full
discovery again only after focused repairs are green and the repo policy allows
another external promotion/nightly/manual lane.
