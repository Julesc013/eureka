# Track B Dependency Map

## Present As Contracts

- `node_manifest`: `contracts/node/eureka_node_manifest.v0.json`
- `node_policy`: `contracts/node/node_policy.v0.json`
- `node_capability_future`: `contracts/node/node_capability.v0.json`
- `workunit_contract_future`: `contracts/node/work_unit.v0.json`
- `workunit_result_contract_future`: `contracts/node/work_unit_result.v0.json`
- `local_foundry_state_future`: `contracts/node/local_foundry_state.v0.json`

Contract presence is not runtime activation.

## Future Or Deferred Runtime Dependencies

- `candidate_store_future`
- `review_queue_future`
- `source_cache_future`
- `evidence_ledger_future`
- `node_policy_evaluator_future`
- `workunit_dry_run_runner_future`

## Current Alignment

- OBS WorkUnit seeds can be reviewed against the Track B WorkUnit and WorkUnit result contract shape.
- OBS SearchNeed seeds still need future Track B acceptance semantics before runtime use.
- Source policy decisions remain separate from node policy contract presence.
