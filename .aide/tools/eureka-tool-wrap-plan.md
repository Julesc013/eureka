# Eureka Tool Wrap Plan

- Source inventory: `.aide/tools/latest-tool-inventory.json`
- Candidate count: 2164
- Wrapper count: 14
- Q56 execution allowed: false
- Q56 apply allowed: false
- Rule: discover -> classify -> wrap -> adapt -> migrate -> retire with evidence.

| Wrapper ID | Source Tool | Proposed Command | Capability | Risk | Q56 Execution |
|---|---|---|---|---|---|
| `eureka.validate.architecture` | `scripts/check_architecture_boundaries.py` | `eureka.validate.architecture` | architecture_policy | authority_sensitive | false |
| `eureka.validate.source_cache_contract` | `scripts/validate_source_cache_contract.py` | `eureka.validate.source_cache_contract` | source_policy | source_mutation_sensitive | false |
| `eureka.validate.source_cache_to_evidence` | `scripts/validate_source_cache_evidence_ledger_contract.py` | `eureka.validate.source_cache_to_evidence` | source_policy, evidence_policy | source_mutation_sensitive, evidence_mutation_sensitive | false |
| `eureka.validate.evidence_ledger_contract` | `scripts/validate_evidence_ledger_contract.py` | `eureka.validate.evidence_ledger_contract` | evidence_policy | evidence_mutation_sensitive | false |
| `eureka.validate.public_search_index` | `scripts/validate_public_search_index.py` | `eureka.validate.public_search_index` | index_policy | index_mutation_sensitive | false |
| `eureka.validate.reviewed_public_index` | `scripts/validate_reviewed_public_index.py` | `eureka.validate.reviewed_public_index` | index_policy | index_mutation_sensitive | false |
| `eureka.validate.static_site` | `site/validate.py` | `eureka.validate.static_site` | site_policy | build_sensitive | false |
| `eureka.validate.public_static_site` | `scripts/validate_public_static_site.py` | `eureka.validate.public_static_site` | site_policy | build_sensitive | false |
| `eureka.validate.static_snapshot` | `scripts/validate_static_snapshot.py` | `eureka.validate.static_snapshot` | snapshot_policy | build_sensitive | false |
| `eureka.validate.snapshot_runtime` | `scripts/validate_snapshot_runtime.py` | `eureka.validate.snapshot_runtime` | snapshot_policy | build_sensitive | false |
| `eureka.validate.pack_set` | `scripts/validate_pack_set.py` | `eureka.validate.pack_set` | package | authority_sensitive | false |
| `eureka.validate.connector_approval` | `scripts/validate_connector_approval_runtime_planning_audit.py` | `eureka.validate.connector_approval` | connector_policy | network_sensitive | false |
| `eureka.audit.test_lanes` | `docs/operations/TEST_AND_EVAL_LANES.md` | `eureka.audit.test_lanes` | repo_policy | authority_sensitive | false |
| `eureka.audit.command_matrix` | `control/inventory/tests/command_matrix.json` | `eureka.audit.command_matrix` | repo_policy | authority_sensitive | false |

All wrappers are plans only. Unknown tools remain preserved for manual review; no wrapper runs or migrations are authorized by Q56.
