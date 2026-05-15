# Wrap Plan

Generated source:

- `.aide/tools/latest-tool-wrap-plan.json`
- `.aide/tools/latest-tool-wrap-plan.md`
- `.aide/tools/latest-tool-adapter-map.json`
- `.aide/tools/latest-tool-adapter-map.md`
- `.aide/tools/eureka-tool-adapter-map.json`
- `.aide/tools/eureka-tool-wrap-plan.md`

Q56 wrapper plans are dry-run evidence only:

- `execution_allowed: false`
- `apply_allowed: false`
- `future_phase_required: true`

| Future Wrapper ID | Source Tool Path | Proposed AIDE Command | Contract Hint | Risk Notes |
|---|---|---|---|---|
| `eureka.validate.architecture` | `scripts/check_architecture_boundaries.py` | `eureka.validate.architecture` | run only after reviewed authorization; write structured evidence | authority_sensitive |
| `eureka.validate.source_cache_contract` | `scripts/validate_source_cache_contract.py` | `eureka.validate.source_cache_contract` | read contract and validation outputs only | source_mutation_sensitive |
| `eureka.validate.source_cache_to_evidence` | `scripts/validate_source_cache_evidence_ledger_contract.py` | `eureka.validate.source_cache_to_evidence` | read-only bridge contract validation | source_mutation_sensitive, evidence_mutation_sensitive |
| `eureka.validate.evidence_ledger_contract` | `scripts/validate_evidence_ledger_contract.py` | `eureka.validate.evidence_ledger_contract` | no ledger append/write | evidence_mutation_sensitive |
| `eureka.validate.public_search_index` | `scripts/validate_public_search_index.py` | `eureka.validate.public_search_index` | no public-index rebuild/write | index_mutation_sensitive |
| `eureka.validate.reviewed_public_index` | `scripts/validate_reviewed_public_index.py` | `eureka.validate.reviewed_public_index` | no index rebuild/write | index_mutation_sensitive |
| `eureka.validate.static_site` | `site/validate.py` | `eureka.validate.static_site` | no site deploy/publish | build_sensitive |
| `eureka.validate.public_static_site` | `scripts/validate_public_static_site.py` | `eureka.validate.public_static_site` | no deploy/publish | build_sensitive |
| `eureka.validate.static_snapshot` | `scripts/validate_static_snapshot.py` | `eureka.validate.static_snapshot` | read-only snapshot validation | build_sensitive |
| `eureka.validate.snapshot_runtime` | `scripts/validate_snapshot_runtime.py` | `eureka.validate.snapshot_runtime` | read-only snapshot validation | build_sensitive |
| `eureka.validate.pack_set` | `scripts/validate_pack_set.py` | `eureka.validate.pack_set` | no pack import/export mutation | authority_sensitive |
| `eureka.validate.connector_approval` | `scripts/validate_connector_approval_runtime_planning_audit.py` | `eureka.validate.connector_approval` | no live connector call | network_sensitive |
| `eureka.audit.test_lanes` | `docs/operations/TEST_AND_EVAL_LANES.md` | `eureka.audit.test_lanes` | review-only policy source | authority_sensitive |
| `eureka.audit.command_matrix` | `control/inventory/tests/command_matrix.json` | `eureka.audit.command_matrix` | review-only lane source | authority_sensitive |

Future wrapper validation requirement:

- `tools validate`
- `repo validate`
- `quality validate`
- architecture boundary validation where applicable
- targeted no-network/no-mutation checks for source/evidence/index/connector wrappers

No wrapper is executed or installed by Q56.
