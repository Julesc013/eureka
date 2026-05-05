# Command Results

P76 verification was run locally with no Software Heritage API calls, no SWHID resolution, no origin lookup, no source content/blob fetch, no repository clone, no source archive download, no source cache/evidence ledger mutation, and no public-query fanout.

- passed: 88
- failed: 0
- skipped: 3
- repaired: 1

## P76 approval examples validator

- command: `python scripts/validate_software_heritage_connector_approval.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.09
- summary:
```text
status: valid
example_count: 1
```

## P76 approval examples validator JSON

- command: `python scripts/validate_software_heritage_connector_approval.py --all-examples --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.087
- summary:
```text
{
  "status": "valid",
  "created_by": "software_heritage_connector_approval_validator_v0",
  "example_count": 1,
  "results": [
    {
      "status": "valid",
      "created_by": "software_heritage_connector_approval_validator_v0",
```

## P76 contract validator

- command: `python scripts/validate_software_heritage_connector_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.101
- summary:
```text
status: valid
example_count: 1
contract_file: contracts/connectors/software_heritage_connector_approval.v0.json
```

## P76 contract validator JSON

- command: `python scripts/validate_software_heritage_connector_contract.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.101
- summary:
```text
{
  "status": "valid",
  "created_by": "software_heritage_connector_contract_validator_v0",
  "contract_file": "contracts/connectors/software_heritage_connector_approval.v0.json",
  "example_count": 1,
  "errors": [],
  "warnings": []
}
```

## P76 dry-run approval JSON

- command: `python scripts/dry_run_software_heritage_connector_approval.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.062
- summary:
```text
{
  "schema_version": "0.1.0",
  "approval_record_id": "dry_run.connector.software_heritage.approval.v0",
  "approval_record_kind": "software_heritage_connector_approval",
  "status": "draft_example",
  "created_by_tool": "dry_run_software_heritage_connector_approval_v0",
  "connector_ref": {
    "connector_id": "software_heritage_connector",
```

## P75 approval examples validator

- command: `python scripts/validate_npm_metadata_connector_approval.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.088
- summary:
```text
status: valid
example_count: 1
```

## P75 contract validator

- command: `python scripts/validate_npm_metadata_connector_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.117
- summary:
```text
status: valid
example_count: 1
contract_file: contracts/connectors/npm_metadata_connector_approval.v0.json
```

## P74 approval examples validator

- command: `python scripts/validate_pypi_metadata_connector_approval.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.084
- summary:
```text
status: valid
example_count: 1
```

## P74 contract validator

- command: `python scripts/validate_pypi_metadata_connector_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.109
- summary:
```text
status: valid
example_count: 1
contract_file: contracts/connectors/pypi_metadata_connector_approval.v0.json
```

## P73 approval examples validator

- command: `python scripts/validate_github_releases_connector_approval.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.08
- summary:
```text
status: valid
example_count: 1
```

## P73 contract validator

- command: `python scripts/validate_github_releases_connector_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.119
- summary:
```text
status: valid
example_count: 1
contract_file: contracts/connectors/github_releases_connector_approval.v0.json
```

## P72 approval examples validator

- command: `python scripts/validate_wayback_cdx_memento_connector_approval.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.076
- summary:
```text
status: valid
example_count: 1
```

## P72 contract validator

- command: `python scripts/validate_wayback_cdx_memento_connector_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.103
- summary:
```text
status: valid
example_count: 1
contract_file: contracts/connectors/wayback_cdx_memento_connector_approval.v0.json
```

## P71 approval examples validator

- command: `python scripts/validate_internet_archive_metadata_connector_approval.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.075
- summary:
```text
status: valid
example_count: 1
```

## P71 contract validator

- command: `python scripts/validate_internet_archive_metadata_connector_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.092
- summary:
```text
status: valid
example_count: 1
contract_file: contracts/connectors/internet_archive_metadata_connector_approval.v0.json
```

## Source cache record examples validator

- command: `python scripts/validate_source_cache_record.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.073
- summary:
```text
status: valid
example_count: 3
```

## Source cache contract validator

- command: `python scripts/validate_source_cache_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
status: valid
example_count: 3
contract_file: contracts/source_cache/source_cache_record.v0.json
```

## Evidence ledger record examples validator

- command: `python scripts/validate_evidence_ledger_record.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.071
- summary:
```text
status: valid
example_count: 3
```

## Evidence ledger contract validator

- command: `python scripts/validate_evidence_ledger_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.073
- summary:
```text
status: valid
example_count: 3
contract_file: contracts/evidence_ledger/evidence_ledger_record.v0.json
```

## Source cache/evidence ledger contract validator

- command: `python scripts/validate_source_cache_evidence_ledger_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.078
- summary:
```text
status: valid
report_id: source_cache_evidence_ledger_v0
```

## Source sync worker job examples validator

- command: `python scripts/validate_source_sync_worker_job.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.078
- summary:
```text
status: valid
example_count: 4
```

## Source sync worker contract validator

- command: `python scripts/validate_source_sync_worker_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.123
- summary:
```text
status: valid
contract_file: contracts/source_sync/source_sync_worker_job.v0.json
example_count: 4
```

## Demand dashboard examples validator

- command: `python scripts/validate_demand_dashboard_snapshot.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.076
- summary:
```text
status: valid
example_count: 2
```

## Demand dashboard contract validator

- command: `python scripts/validate_demand_dashboard_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.088
- summary:
```text
status: valid
contract_file: contracts/query/demand_dashboard_snapshot.v0.json
example_count: 2
```

## Query guard examples validator

- command: `python scripts/validate_query_guard_decision.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.077
- summary:
```text
Query Guard Decision validation
status: valid
example_count: 5
warnings:
- examples/query_guard/minimal_fake_demand_throttled_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_private_path_rejected_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_public_safe_query_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_secret_rejected_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
```

## Query privacy poisoning guard contract validator

- command: `python scripts/validate_query_privacy_poisoning_guard_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.084
- summary:
```text
Query Privacy and Poisoning Guard Contract validation
status: valid
contract_file: contracts/query/query_guard_decision.v0.json
report_id: query_privacy_poisoning_guard_v0
example_count: 5
warnings:
- P67 is contract-only; runtime query privacy and poisoning guard remains deferred.
```

## Known absence page examples validator

- command: `python scripts/validate_known_absence_page.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.075
- summary:
```text
Known Absence Page validation
status: valid
example_count: 3
warnings:
- examples/known_absence_pages/minimal_near_miss_absence_v0: P66 validates contract/example artifacts only; runtime known absence pages remain deferred.
- examples/known_absence_pages/minimal_no_verified_result_v0: P66 validates contract/example artifacts only; runtime known absence pages remain deferred.
- examples/known_absence_pages/minimal_policy_blocked_absence_v0: P66 validates contract/example artifacts only; runtime known absence pages remain deferred.
```

## Known absence page contract validator

- command: `python scripts/validate_known_absence_page_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.089
- summary:
```text
Known Absence Page Contract validation
status: valid
contract_file: contracts/query/known_absence_page.v0.json
report_id: known_absence_page_v0
example_count: 3
warnings:
- P66 is contract-only; runtime known absence page serving remains deferred.
```

## Candidate promotion assessment examples validator

- command: `python scripts/validate_candidate_promotion_assessment.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.075
- summary:
```text
Candidate Promotion Assessment validation
status: valid
example_count: 4
```

## Candidate promotion policy validator

- command: `python scripts/validate_candidate_promotion_policy.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.084
- summary:
```text
Candidate Promotion Policy validation
status: valid
contract_file: contracts/query/candidate_promotion_assessment.v0.json
report_id: candidate_promotion_policy_v0
example_count: 4
warnings:
- P65 is contract-only; candidate promotion runtime remains deferred.
```

## Candidate index record examples validator

- command: `python scripts/validate_candidate_index_record.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Candidate Index Record validation
status: valid
example_count: 4
```

## Candidate index contract validator

- command: `python scripts/validate_candidate_index_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.077
- summary:
```text
Candidate Index Contract validation
status: valid
contract_file: contracts/query/candidate_index_record.v0.json
report_id: candidate_index_v0
example_count: 4
warnings:
- P64 is contract-only; candidate index runtime and promotion remain deferred.
```

## Probe queue item examples validator

- command: `python scripts/validate_probe_queue_item.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.073
- summary:
```text
Probe Queue Item validation
status: valid
example_count: 3
```

## Probe queue contract validator

- command: `python scripts/validate_probe_queue_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.075
- summary:
```text
Probe Queue Contract validation
status: valid
contract_file: contracts/query/probe_queue_item.v0.json
report_id: probe_queue_v0
example_count: 3
warnings:
- P63 is contract-only; probe queue runtime and probe execution remain deferred.
```

## Search need record examples validator

- command: `python scripts/validate_search_need_record.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.073
- summary:
```text
Search Need Record validation
status: valid
example_count: 2
```

## Search need record contract validator

- command: `python scripts/validate_search_need_record_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Search Need Record Contract validation
status: valid
contract_file: contracts/query/search_need_record.v0.json
report_id: search_need_record_v0
example_count: 2
warnings:
- P62 is contract-only; search need runtime storage remains deferred.
```

## Search miss ledger entry examples validator

- command: `python scripts/validate_search_miss_ledger_entry.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.073
- summary:
```text
Search Miss Ledger Entry validation
status: valid
example_count: 2
```

## Search miss ledger contract validator

- command: `python scripts/validate_search_miss_ledger_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Search Miss Ledger Contract validation
status: valid
contract_file: contracts/query/search_miss_ledger_entry.v0.json
report_id: search_miss_ledger_v0
example_count: 2
warnings:
- P61 is contract-only; miss ledger runtime writes remain deferred.
```

## Search result cache entry examples validator

- command: `python scripts/validate_search_result_cache_entry.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Search Result Cache Entry validation
status: valid
example_count: 2
```

## Shared query result cache contract validator

- command: `python scripts/validate_shared_query_result_cache_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.073
- summary:
```text
Shared Query/Result Cache Contract validation
status: valid
contract_file: contracts/query/search_result_cache_entry.v0.json
report_id: shared_query_result_cache_v0
example_count: 2
warnings:
- P60 is contract-only; runtime cache reads/writes remain deferred.
```

## Query observation examples validator

- command: `python scripts/validate_query_observation.py --all-examples`
- status: passed
- exit_code: 0
- duration_seconds: 0.069
- summary:
```text
Query Observation validation
status: valid
example_count: 1
```

## Query observation contract validator

- command: `python scripts/validate_query_observation_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.072
- summary:
```text
Query Observation Contract validation
status: valid
contract_file: contracts/query/query_observation.v0.json
report_id: query_observation_contract_v0
example_count: 1
warnings:
- P59 is contract-only; runtime query observation collection remains deferred.
```

## Live probe gateway validator

- command: `python scripts/validate_live_probe_gateway.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.248
- summary:
```text
Live probe gateway validation
status: valid
candidate_sources: 9
disabled_sources: 9
wrapper_live_probes_enabled: False
wrapper_live_internet_archive_enabled: False
```

## Hosted public search rehearsal runner

- command: `python scripts/run_hosted_public_search_rehearsal.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.991
- summary:
```text
Hosted Public Search Rehearsal
status: passed
mode: hosted_local_rehearsal
base_url: http://127.0.0.1:58995
server_started: True
checks: 60/60
safe routes: 9
safe queries: 5
```

## Hosted public search rehearsal validator

- command: `python scripts/validate_hosted_public_search_rehearsal.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.92
- summary:
```text
Hosted Public Search Rehearsal validation
status: valid
report_id: hosted_public_search_rehearsal_v0
routes: 9
safe_queries: 5
blocked_requests: 34
live_rehearsal_status: passed
warnings:
```

## Public search safety evidence runner

- command: `python scripts/run_public_search_safety_evidence.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.413
- summary:
```text
Public Search Safety Evidence
status: passed
mode: local_index_only
checks: 64/64
safe routes: 9
safe queries: 4
blocked requests: 32/32
public index documents: 584
```

## Public search safety evidence validator

- command: `python scripts/validate_public_search_safety_evidence.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.424
- summary:
```text
Public Search Safety Evidence validation
status: valid
report_id: public_search_safety_evidence_v0
safe_query_count: 4
blocked_request_count: 32
```

## Static site search integration validator

- command: `python scripts/validate_static_site_search_integration.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Static Site Search Integration validation
status: valid
report_id: static_site_search_integration_v0
backend_status: backend_unconfigured
document_count: 584
```

## Public search index builder validator

- command: `python scripts/validate_public_search_index_builder.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.788
- summary:
```text
Public Search Index Builder validation
status: valid
report_id: public_search_index_builder_v0
document_count: 584
```

## Public search index validator

- command: `python scripts/validate_public_search_index.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.265
- summary:
```text
Public Search Index validation
status: valid
index_root: data/public_index
document_count: 584
private_paths_detected: False
```

## Hosted public search wrapper validator

- command: `python scripts/validate_hosted_public_search_wrapper.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.279
- summary:
```text
Hosted public search wrapper validation
status: valid
report_id: hosted_public_search_wrapper_v0
public_search_mode: local_index_only
hosted_wrapper_implemented: True
hosted_backend_deployed: False
hosted_deployment_verified: False
```

## Hosted public search wrapper check

- command: `python scripts/check_hosted_public_search_wrapper.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.274
- summary:
```text
Hosted public search wrapper check
status: passed
mode: local_index_only
checks: 14/14
- PASS check_config: Safe defaults accepted.
- PASS healthz: OK
- PASS status_top_level: OK
- PASS status_api: OK
```

## Hosted public search config check

- command: `python scripts/run_hosted_public_search.py --check-config`
- status: passed
- exit_code: 0
- duration_seconds: 0.232
- summary:
```text
Hosted public search wrapper config
status: valid
host: 127.0.0.1
port: 8080
mode: local_index_only
hosted_deployment_verified: False
live_probes_enabled: False
downloads_enabled: False
```

## Public search production contract validator

- command: `python scripts/validate_public_search_production_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.077
- summary:
```text
Public search production contract validation
status: valid
report_id: public_search_production_contract_v0
active_mode: local_index_only
hosted_search_implemented: False
live_probes_enabled: False
```

## Static deployment evidence validator

- command: `python scripts/validate_static_deployment_evidence.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.068
- summary:
```text
Static deployment evidence validation
status: valid
report_id: static_deployment_evidence_v0
artifact_root: site/dist
workflow_path: .github/workflows/pages.yml
deployment_verified: False
deployment_success_claimed: False
```

## Post-P50 remediation validator

- command: `python scripts/validate_post_p50_remediation.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.068
- summary:
```text
post-p50 remediation validation passed: 17 required files checked
```

## Post-P49 platform audit validator

- command: `python scripts/validate_post_p49_platform_audit.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.068
- summary:
```text
post-p49 platform audit validation passed: 28 required files checked
```

## Public search contract validator

- command: `python scripts/validate_public_search_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Public search contract validation
status: valid
contract_id: public_search_api_contract_v0
first_allowed_mode: local_index_only
runtime_routes_implemented: True
registered_routes: 6
forbidden_parameters: 26
```

## Public search result-card contract validator

- command: `python scripts/validate_public_search_result_card_contract.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.07
- summary:
```text
status: valid
contract_id: public_search_result_card_contract_v0
schema: contracts/api/search_result_card.v0.json
response_schema: contracts/api/search_response.v0.json
audit_pack: control/audits/public-search-result-card-contract-v0
examples: 5
```

## Public search safety validator

- command: `python scripts/validate_public_search_safety.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.07
- summary:
```text
Public Search Safety / Abuse Guard validation
status: valid
safety_policy_id: eureka-public-search-safety-abuse-guard-v0
first_allowed_mode: local_index_only
max_query_length: 160
max_result_limit: 25
max_runtime_ms_contract: 3000
telemetry_default: off
```

## Local public search runtime validator

- command: `python scripts/validate_local_public_search_runtime.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.068
- summary:
```text
Local Public Search Runtime validation
status: valid
runtime_scope: local_prototype_backend
mode: local_index_only
routes: 6
hosted_public_deployment: False
static_search_handoff: True
```

## Public search smoke

- command: `python scripts/public_search_smoke.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.55
- summary:
```text
Public Search Smoke
status: passed
mode: local_index_only
checks: 30/30 passed
safe queries: 9
blocked requests: 14

[PASS] status: /api/v1/status (ok)
```

## Public search smoke JSON

- command: `python scripts/public_search_smoke.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.544
- summary:
```text
{
  "base_runtime_slice": "local_public_search_runtime_v0",
  "blocked_request_results": [
    {
      "actual_error_code": "query_required",
      "expected_error_code": "query_required",
      "message": "Check passed.",
      "name": "missing q",
```

## Public search index builder check

- command: `python scripts/build_public_search_index.py --check`
- status: passed
- exit_code: 0
- duration_seconds: 0.483
- summary:
```text
Public Search Index Builder v0
status: valid
output_root: data/public_index
document_count: 584
fts5_available: True
fts5_enabled: False
fallback_enabled: True
```

## Static site build check

- command: `python site/build.py --check`
- status: passed
- exit_code: 0
- duration_seconds: 0.918
- summary:
```text
Static site generator
status: valid
source_root: site
deploy_artifact_current: site/dist
```

## Static site validate

- command: `python site/validate.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.098
- summary:
```text
Static site generator validation
status: valid
page_count: 9
dist_validation: valid
```

## Publication inventory validator

- command: `python scripts/validate_publication_inventory.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.074
- summary:
```text
Publication inventory validation
status: valid
registered_routes: 51
current_static_artifact_pages: 9
required_client_profiles: 9
required_public_data_paths: 14
```

## Public static site validator

- command: `python scripts/validate_public_static_site.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.09
- summary:
```text
Public static site validation
status: valid
pages: 9
source_ids_checked: 15
```

## GitHub Pages static artifact checker

- command: `python scripts/check_github_pages_static_artifact.py --path site/dist`
- status: passed
- exit_code: 0
- duration_seconds: 0.161
- summary:
```text
GitHub Pages static artifact check
status: valid
site_dir: <repo>\site\dist
static_site_validator: valid
publication_inventory_validator: valid
```

## Generated artifact drift check

- command: `python scripts/check_generated_artifact_drift.py`
- status: passed
- exit_code: 0
- duration_seconds: 9.096
- summary:
```text
Generated Artifact Drift Guard v0
status: valid
inventory: control/inventory/generated_artifacts/generated_artifacts.json
policy: control/inventory/generated_artifacts/drift_policy.json
strict: False
status_counts: {'passed': 12}
- public_data_summaries: passed
  - check_command: passed (python scripts/generate_public_data_summaries.py --check)
```

## Public alpha smoke

- command: `python scripts/public_alpha_smoke.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.591
- summary:
```text
Public Alpha Smoke
status: passed
mode: public_alpha
checks: 18/18 passed

[PASS] status: /api/status (ok)
[PASS] source list: /api/sources (ok)
[PASS] query plan: /api/query-plan?q=Windows+7+apps (ok)
```

## Archive resolution evals

- command: `python scripts/run_archive_resolution_evals.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.322
- summary:
```text
Archive resolution evals
created_by_slice: archive_resolution_eval_runner_v0
task_count: 6
status_counts: satisfied=6

Tasks
- article_inside_magazine_scan: satisfied (planner=satisfied, search=local_index, results=9)
- driver_inside_support_cd: satisfied (planner=satisfied, search=local_index, results=50)
```

## Archive resolution evals JSON

- command: `python scripts/run_archive_resolution_evals.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.33
- summary:
```text
{
  "created_at": "2026-05-05T10:09:29.040557+00:00",
  "created_by_slice": "archive_resolution_eval_runner_v0",
  "load_errors": [],
  "notices": [
    {
      "code": "transient_local_index",
      "message": "Built a transient Local Index v0 database for this eval run. The report omits the temporary path so JSON remains inspectable.",
```

## Search usefulness audit

- command: `python scripts/run_search_usefulness_audit.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.359
- summary:
```text
Search usefulness audit
created_by_slice: search_usefulness_audit_v0
query_count: 64
eureka_status_counts: capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2
external_pending_counts: google=64, internet_archive_full_text=64, internet_archive_metadata=64
failure_mode_counts: absence_reasoning_gap=2, actionability_gap=2, compatibility_evidence_gap=25, decomposition_gap=12, external_baseline_pending=64, identity_cluster_gap=14, index_gap=2, live_source_gap=10, member_access_gap=12, planner_gap=24, query_interpretation_gap=21, ranking_gap=9, representation_gap=14, source_coverage_gap=49, surface_ux_gap=4

Top future-work recommendations
```

## Search usefulness audit JSON

- command: `python scripts/run_search_usefulness_audit.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.376
- summary:
```text
{
  "created_at": "2026-05-05T10:09:29.764600+00:00",
  "created_by_slice": "search_usefulness_audit_v0",
  "eureka_status_counts": {
    "capability_gap": 7,
    "covered": 5,
    "partial": 40,
    "source_gap": 10,
```

## External baseline status JSON

- command: `python scripts/report_external_baseline_status.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.069
- summary:
```text
{
  "batches": {
    "batch_0": {
      "completion_percent": 0.0,
      "directory": "<repo>\\evals\\search_usefulness\\external_baselines\\batches\\batch_0",
      "expected_observation_count": 39,
      "missing_observation_slots": [],
      "next_pending_slots": [
```

## Python oracle golden check

- command: `python scripts/generate_python_oracle_golden.py --check`
- status: passed
- exit_code: 0
- duration_seconds: 0.837
- summary:
```text
Python oracle golden fixture pack
status: passed
fixture_pack_id: python_oracle_golden_v0
fixture_pack_version: 0.1.0
output_root: <repo>\tests\parity\golden\python_oracle\v0
file_count: 40
```

## Unittest tests/scripts

- command: `python -m unittest discover -s tests/scripts -t .`
- status: passed
- exit_code: 0
- duration_seconds: 105.182
- summary:
```text
stderr: .................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
stderr: ----------------------------------------------------------------------
stderr: Ran 481 tests in 105.018s
stderr: 
stderr: OK
```

## Unittest tests/operations

- command: `python -m unittest discover -s tests/operations -t .`
- status: passed
- exit_code: 0
- duration_seconds: 8.664
- summary:
```text
stderr: ............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
stderr: ----------------------------------------------------------------------
stderr: Ran 524 tests in 8.382s
stderr: 
stderr: OK
```

## Unittest tests/hardening

- command: `python -m unittest discover -s tests/hardening -t .`
- status: passed
- exit_code: 0
- duration_seconds: 5.419
- summary:
```text
stderr: .....................................................
stderr: ----------------------------------------------------------------------
stderr: Ran 53 tests in 5.189s
stderr: 
stderr: OK
```

## Unittest tests/parity

- command: `python -m unittest discover -s tests/parity -t .`
- status: passed
- exit_code: 0
- duration_seconds: 1.402
- summary:
```text
stderr: .........................
stderr: ----------------------------------------------------------------------
stderr: Ran 25 tests in 1.320s
stderr: 
stderr: OK
```

## Unittest runtime

- command: `python -m unittest discover -s runtime -t .`
- status: passed
- exit_code: 0
- duration_seconds: 4.88
- summary:
```text
stderr: ................................................................................................................................................................................................................................................................................................................................
stderr: ----------------------------------------------------------------------
stderr: Ran 320 tests in 4.602s
stderr: 
stderr: OK
```

## Unittest surfaces

- command: `python -m unittest discover -s surfaces -t .`
- status: passed
- exit_code: 0
- duration_seconds: 30.408
- summary:
```text
stderr: ........................................................................................................................................................................
stderr: ----------------------------------------------------------------------
stderr: Ran 168 tests in 30.159s
stderr: 
stderr: OK
```

## Unittest all tests

- command: `python -m unittest discover -s tests -t .`
- status: passed
- exit_code: 0
- duration_seconds: 126.76
- summary:
```text
stderr: ......................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
stderr: ----------------------------------------------------------------------
stderr: Ran 1174 tests in 126.382s
stderr: 
stderr: OK
```

## Architecture boundary check

- command: `python scripts/check_architecture_boundaries.py`
- status: passed
- exit_code: 0
- duration_seconds: 0.482
- summary:
```text
Checked 446 Python files under <repo>
No architecture-boundary violations found.
```

## Git diff check

- command: `git diff --check`
- status: repaired
- exit_code: 2
- duration_seconds: 0.102
- summary:
```text
.aide/commands/ci.yaml:768: new blank line at EOF.
.aide/commands/dev.yaml:1144: new blank line at EOF.
scripts/README.md:735: new blank line at EOF.
stderr: warning: in the working copy of 'site/dist/assets/site.css', LF will be replaced by CRLF the next time Git touches it
stderr: warning: in the working copy of 'site/dist/demo/README.txt', LF will be replaced by CRLF the next time Git touches it
stderr: warning: in the working copy of 'site/dist/demo/absence-example.html', LF will be replaced by CRLF the next time Git touches it
stderr: warning: in the working copy of 'site/dist/demo/comparison-example.html', LF will be replaced by CRLF the next time Git touches it
stderr: warning: in the working copy of 'site/dist/demo/data/demo_snapshots.json', LF will be replaced by CRLF the next time Git touches it
Follow-up: trailing blank lines were removed from .aide/commands/ci.yaml, .aide/commands/dev.yaml, and scripts/README.md; rerun passed.
```

## Git diff check rerun after whitespace repair

- command: `git diff --check`
- status: passed
- exit_code: 0
- duration_seconds: 0.087
- summary:
```text
stderr: warning: in the working copy of '.aide/commands/ci.yaml', LF will be replaced by CRLF the next time Git touches it
stderr: warning: in the working copy of '.aide/commands/dev.yaml', LF will be replaced by CRLF the next time Git touches it
stderr: warning: in the working copy of 'scripts/README.md', LF will be replaced by CRLF the next time Git touches it
```

## P76 contract validator rerun after command evidence update

- command: `python scripts/validate_software_heritage_connector_contract.py --json`
- status: passed
- exit_code: 0
- duration_seconds: 0.108
- summary:
```text
{
  "status": "valid",
  "created_by": "software_heritage_connector_contract_validator_v0",
  "contract_file": "contracts/connectors/software_heritage_connector_approval.v0.json",
  "example_count": 1,
  "errors": [],
  "warnings": []
}
```

## Git status after verification

- command: `git status --short --branch`
- status: passed
- exit_code: 0
- duration_seconds: 0.061
- summary:
```text
## main...origin/main
 M .aide/commands/ci.yaml
 M .aide/commands/dev.yaml
 M .aide/reports/README.md
 M .aide/tasks/audit_backlog.yaml
 M .aide/tasks/queue.yaml
 M contracts/connectors/README.md
 M control/audits/README.md
```

## Cargo version optional check

- command: `cargo --version`
- status: skipped
- exit_code: None
- duration_seconds: 0.0
- summary:
```text
cargo is not available in this PowerShell environment.
```

## Cargo workspace check optional

- command: `cargo check --workspace --manifest-path crates/Cargo.toml`
- status: skipped
- exit_code: None
- duration_seconds: 0.0
- summary:
```text
not run because cargo is unavailable locally.
```

## Cargo workspace test optional

- command: `cargo test --workspace --manifest-path crates/Cargo.toml`
- status: skipped
- exit_code: None
- duration_seconds: 0.0
- summary:
```text
not run because cargo is unavailable locally.
```
