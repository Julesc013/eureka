# Artifact Taxonomy Summary

- Artifact count: `14823`

## Artifact Kinds
- `artifact_existence_test`: `383`
- `audit_contract`: `189`
- `audit_evidence`: `4225`
- `documentation`: `1993`
- `domain_contract`: `189`
- `fixture_contract`: `2174`
- `fixture_runtime`: `272`
- `generated_scaffold`: `1`
- `integration_test`: `84`
- `operator_script`: `267`
- `policy_contract`: `1009`
- `preview_contract`: `1795`
- `preview_runtime`: `146`
- `production_runtime`: `403`
- `prototype_runtime`: `620`
- `public_api_contract`: `33`
- `queue_or_task_control`: `389`
- `runtime_contract`: `1`
- `unit_test`: `312`
- `unknown`: `20`
- `validator`: `318`

## Maturity
- `audit_only`: `7447`
- `behavior_implemented`: `1214`
- `empty_or_zero_byte`: `20`
- `fixture_only`: `2669`
- `live_test_ready`: `1`
- `placeholder`: `90`
- `policy_only`: `1708`
- `preview_only`: `1330`
- `unknown`: `344`

## Recommended Actions
- `delete_if_unreferenced`: `69`
- `investigate`: `3624`
- `keep`: `2951`
- `keep_as_control`: `4931`
- `keep_as_fixture_oracle`: `2133`
- `move_to_control`: `409`
- `quarantine`: `390`
- `refactor`: `283`
- `rewrite`: `33`

## Warnings
- 4347 architecture leakage findings in production-looking paths
- 110 placeholder or empty artifacts found
- runtime contains fixture or preview artifacts that should not be treated as product completion
