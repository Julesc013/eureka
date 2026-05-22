# Workbench Review Promote Runbook

Run the dry-run operator preview:

```bash
python scripts/eureka_workbench_review_promote.py --from-fixtures --decision accept_local_reviewed --dry-run --projection operator_workbench --json
```

Verify public and native projections are read-only:

```bash
python scripts/eureka_workbench_review_promote.py --from-fixtures --decision accept_local_reviewed --dry-run --projection public_web --json
python scripts/eureka_workbench_review_promote.py --from-fixtures --decision accept_local_reviewed --dry-run --projection native_desktop_read_only --json
```

Run the temp reviewed-index proof:

```bash
python scripts/eureka_workbench_review_promote.py --from-fixtures --decision accept_local_reviewed --operator-token local-dev-token --use-temp-instance --apply-to-temp --projection operator_workbench --json
```

The temp proof must report `operator_instance_mutated: false`, `master_index_mutated: false`, and `committed_data_public_index_mutated: false`.
