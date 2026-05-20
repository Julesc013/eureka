# Test and Validation Architecture

Eureka uses lane-based validation so routine commits stay fast while promotion
gates remain strict.

The architecture has four governed inputs:

- test lane policy in `control/policies/test_lane_policy.json`
- lane matrix in `control/inventory/test_lane_matrix.json`
- path impact map in `control/inventory/test_impact_map.json`
- failure ledger in `control/inventory/test_failure_ledger.json`

The selector at `scripts/eureka_test_select.py` reads those records and emits a
`test_selection_result.v0` packet. The packet records selected commands, skipped
commands, skip reasons, known failures, failed-first commands, and whether full
discovery is required.

Full unittest discovery is not the default per-commit gate. It remains mandatory
for main promotion, release candidates, large runtime refactors, schema or store
migrations, and pre-public deployment gates.

No selector output is product truth. It is repo-governance evidence only.

