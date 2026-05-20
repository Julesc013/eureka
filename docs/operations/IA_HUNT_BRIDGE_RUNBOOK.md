# IA Hunt Bridge Runbook

Use the bridge in dry-run mode unless a task explicitly requires temp-instance proof.

## Dry-Run

```bash
python scripts/eureka_ia_hunt_bridge.py --query sampleproject --from-fixtures --dry-run --projection operator_workbench --json
```

Dry-run mode creates the Hunt reference, IA WorkUnits, local fixture-backed pipeline packets, result lanes, and a boundary report. It does not mutate stores.

## Temp-Instance Proof

```bash
python scripts/eureka_ia_hunt_bridge.py --query sampleproject --from-fixtures --use-temp-instance --apply-to-temp --projection operator_workbench --json
```

Temp-instance mode writes only under a temporary instance path managed by the command. It may apply source-cache, evidence, candidate index, review queue, and reviewed local index writes to prove the bridge can orchestrate the existing IA pipeline. Operator instance state, master index state, committed `data/public_index`, and public surfaces remain untouched.

## Projection Checks

```bash
python scripts/eureka_ia_hunt_bridge.py --query sampleproject --from-fixtures --dry-run --projection public_web --json
python scripts/eureka_ia_hunt_bridge.py --query sampleproject --from-fixtures --dry-run --projection native_desktop_read_only --json
```

Public and native read-only projections are result-lane projections only. They do not grant review, rebuild, source-probe, download, extraction, model, deployment, or master-index actions.

## Validation

```bash
python scripts/validate_ia_hunt_bridge.py
python scripts/validate_workbench_result_lanes.py
python scripts/validate_search_interaction_contract.py
python scripts/validate_workbench_foundation.py
python scripts/validate_test_lane_policy.py
python scripts/validate_contract_taxonomy.py
python scripts/validate_repo_structure_canon.py
```

Use the test lane router during development:

```bash
python scripts/eureka_test_select.py --changed --failed-first --json
```

Run full unittest discovery at closeout for this runtime orchestration batch.

## Stop Conditions

Stop if the bridge would require live source probing, downloads, extraction, model/provider calls, deployment, operator instance mutation outside explicit temp-instance proof, master-index mutation, force-push, rebase, history rewrite, or production/public launch claims.
