# SYN Foundation Runbook

This runbook validates the Synthetic Query Foundry foundation.

## Local Validation

Run the validator:

```text
python scripts/validate_syn_foundation.py
```

Run focused tests:

```text
python -m unittest tests.scripts.test_validate_syn_foundation
python -m unittest tests.operations.test_syn_foundation
```

Run adjacent contract and seed checks:

```text
python -m unittest tests.contracts.test_search_need_seed_contracts
python -m unittest tests.contracts.test_workunit_seed_contracts
python scripts/validate_search_need_seed_candidates.py
python scripts/validate_workunit_seed_candidates.py
python scripts/validate_ia_hunt_bridge.py
python scripts/validate_workbench_result_lanes.py
```

Use the test selector during development:

```text
python scripts/eureka_test_select.py --changed --failed-first --json
```

## Expected Posture

All SYN artifacts are example-only and planning-only. They should validate:

- demo, hard, and adversarial query sets exist
- every query case has SearchNeed and WorkUnit seed mappings
- expected result lanes cover reviewed, IA metadata, source-cache, review, absence, blocked, running, deferred, and future extraction posture
- safety flags remain false

## Do Not Execute

Do not run source probes, downloads, extraction, model/provider calls, live IA calls, deployments, public fanout, operator instance mutation, master-index mutation, or production/public launch readiness work from this foundation.
