# Command Results

Passed: 83
Skipped: 3
Failed: 0

## python scripts/validate_pypi_metadata_connector_approval.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 1
```

## python scripts/validate_pypi_metadata_connector_approval.py --all-examples --json
status: passed

stdout summary:
```
{
  "status": "valid",
  "created_by": "pypi_metadata_connector_approval_validator_v0",
  "example_count": 1,
  "results": [
    {
      "status": "valid",
      "created_by": "pypi_metadata_connector_approval_validator_v0",
      "approval": "examples\\connectors\\pypi_metadata_approval_v0\\PYPI_METADATA_CONNECTOR_APPROVAL.json",
      "approval_record_id": "example.connector.pypi_metadata.approval.v0",
      "errors": [],
      "warnings": [],
      "approval_root": "examples\\connectors\\pypi_metadata_approval_v0"
    }
  ],
  "errors": [],
  "warnings": []
}
```

## python scripts/validate_pypi_metadata_connector_contract.py
status: passed

stdout summary:
```
status: valid
example_count: 1
contract_file: contracts/connectors/pypi_metadata_connector_approval.v0.json
```

## python scripts/validate_pypi_metadata_connector_contract.py --json
status: passed

stdout summary:
```
{
  "status": "valid",
  "created_by": "pypi_metadata_connector_contract_validator_v0",
  "contract_file": "contracts/connectors/pypi_metadata_connector_approval.v0.json",
  "example_count": 1,
  "errors": [],
  "warnings": []
}
```

## python scripts/dry_run_pypi_metadata_connector_approval.py --json
status: passed

stdout summary:
```
{
  "schema_version": "0.1.0",
  "approval_record_id": "dry_run.connector.pypi_metadata.approval.v0",
  "approval_record_kind": "pypi_metadata_connector_approval",
  "status": "draft_example",
  "created_by_tool": "dry_run_pypi_metadata_connector_approval_v0",
  "connector_ref": {
    "connector_id": "pypi_metadata_connector",
    "connector_label": "PyPI metadata connector",
    "source_family": "pypi",
    "connector_version": "dry-run",
    "source_inventory_ref": "control/inventory/sources/package-registry-recorded-fixtures.source.json",
    "source_status": "approval_required",
    "limitations": [
      "Dry-run only; no live connector execution."
    ]
  },
  "approval_checklist_status": "pending",
  "operator_checklist_status": "pending",
  "package_identity_review_required": true,
```

## python scripts/validate_github_releases_connector_approval.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 1
```

## python scripts/validate_github_releases_connector_contract.py
status: passed

stdout summary:
```
status: valid
example_count: 1
contract_file: contracts/connectors/github_releases_connector_approval.v0.json
```

## python scripts/validate_wayback_cdx_memento_connector_approval.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 1
```

## python scripts/validate_wayback_cdx_memento_connector_contract.py
status: passed

stdout summary:
```
status: valid
example_count: 1
contract_file: contracts/connectors/wayback_cdx_memento_connector_approval.v0.json
```

## python scripts/validate_internet_archive_metadata_connector_approval.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 1
```

## python scripts/validate_internet_archive_metadata_connector_contract.py
status: passed

stdout summary:
```
status: valid
example_count: 1
contract_file: contracts/connectors/internet_archive_metadata_connector_approval.v0.json
```

## python scripts/validate_source_cache_record.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 3
```

## python scripts/validate_source_cache_contract.py
status: passed

stdout summary:
```
status: valid
example_count: 3
contract_file: contracts/source_cache/source_cache_record.v0.json
```

## python scripts/validate_evidence_ledger_record.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 3
```

## python scripts/validate_evidence_ledger_contract.py
status: passed

stdout summary:
```
status: valid
example_count: 3
contract_file: contracts/evidence_ledger/evidence_ledger_record.v0.json
```

## python scripts/validate_source_cache_evidence_ledger_contract.py
status: passed

stdout summary:
```
status: valid
report_id: source_cache_evidence_ledger_v0
```

## python scripts/validate_source_sync_worker_job.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 4
```

## python scripts/validate_source_sync_worker_contract.py
status: passed

stdout summary:
```
status: valid
contract_file: contracts/source_sync/source_sync_worker_job.v0.json
example_count: 4
```

## python scripts/validate_demand_dashboard_snapshot.py --all-examples
status: passed

stdout summary:
```
status: valid
example_count: 2
```

## python scripts/validate_demand_dashboard_contract.py
status: passed

stdout summary:
```
status: valid
contract_file: contracts/query/demand_dashboard_snapshot.v0.json
example_count: 2
```

## python scripts/validate_query_guard_decision.py --all-examples
status: passed

stdout summary:
```
Query Guard Decision validation
status: valid
example_count: 5
warnings:
- examples/query_guard/minimal_fake_demand_throttled_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_private_path_rejected_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_public_safe_query_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_secret_rejected_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
- examples/query_guard/minimal_source_stuffing_quarantined_v0: P67 validates contract/example artifacts only; runtime query guard remains deferred.
```

## python scripts/validate_query_privacy_poisoning_guard_contract.py
status: passed

stdout summary:
```
Query Privacy and Poisoning Guard Contract validation
status: valid
contract_file: contracts/query/query_guard_decision.v0.json
report_id: query_privacy_poisoning_guard_v0
example_count: 5
warnings:
- P67 is contract-only; runtime query privacy and poisoning guard remains deferred.
```

## python scripts/validate_known_absence_page.py --all-examples
status: passed

stdout summary:
```
Known Absence Page validation
status: valid
example_count: 3
warnings:
- examples/known_absence_pages/minimal_near_miss_absence_v0: P66 validates contract/example artifacts only; runtime known absence pages remain deferred.
- examples/known_absence_pages/minimal_no_verified_result_v0: P66 validates contract/example artifacts only; runtime known absence pages remain deferred.
- examples/known_absence_pages/minimal_policy_blocked_absence_v0: P66 validates contract/example artifacts only; runtime known absence pages remain deferred.
```

## python scripts/validate_known_absence_page_contract.py
status: passed

stdout summary:
```
Known Absence Page Contract validation
status: valid
contract_file: contracts/query/known_absence_page.v0.json
report_id: known_absence_page_v0
example_count: 3
warnings:
- P66 is contract-only; runtime known absence page serving remains deferred.
```

## python scripts/validate_candidate_promotion_assessment.py --all-examples
status: passed

stdout summary:
```
Candidate Promotion Assessment validation
status: valid
example_count: 4
```

## python scripts/validate_candidate_promotion_policy.py
status: passed

stdout summary:
```
Candidate Promotion Policy validation
status: valid
contract_file: contracts/query/candidate_promotion_assessment.v0.json
report_id: candidate_promotion_policy_v0
example_count: 4
warnings:
- P65 is contract-only; candidate promotion runtime remains deferred.
```

## python scripts/validate_candidate_index_record.py --all-examples
status: passed

stdout summary:
```
Candidate Index Record validation
status: valid
example_count: 4
```

## python scripts/validate_candidate_index_contract.py
status: passed

stdout summary:
```
Candidate Index Contract validation
status: valid
contract_file: contracts/query/candidate_index_record.v0.json
report_id: candidate_index_v0
example_count: 4
warnings:
- P64 is contract-only; candidate index runtime and promotion remain deferred.
```

## python scripts/validate_probe_queue_item.py --all-examples
status: passed

stdout summary:
```
Probe Queue Item validation
status: valid
example_count: 3
```

## python scripts/validate_probe_queue_contract.py
status: passed

stdout summary:
```
Probe Queue Contract validation
status: valid
contract_file: contracts/query/probe_queue_item.v0.json
report_id: probe_queue_v0
example_count: 3
warnings:
- P63 is contract-only; probe queue runtime and probe execution remain deferred.
```

## python scripts/validate_search_need_record.py --all-examples
status: passed

stdout summary:
```
Search Need Record validation
status: valid
example_count: 2
```

## python scripts/validate_search_need_record_contract.py
status: passed

stdout summary:
```
Search Need Record Contract validation
status: valid
contract_file: contracts/query/search_need_record.v0.json
report_id: search_need_record_v0
example_count: 2
warnings:
- P62 is contract-only; search need runtime storage remains deferred.
```

## python scripts/validate_search_miss_ledger_entry.py --all-examples
status: passed

stdout summary:
```
Search Miss Ledger Entry validation
status: valid
example_count: 2
```

## python scripts/validate_search_miss_ledger_contract.py
status: passed

stdout summary:
```
Search Miss Ledger Contract validation
status: valid
contract_file: contracts/query/search_miss_ledger_entry.v0.json
report_id: search_miss_ledger_v0
example_count: 2
warnings:
- P61 is contract-only; miss ledger runtime writes remain deferred.
```

## python scripts/validate_search_result_cache_entry.py --all-examples
status: passed

stdout summary:
```
Search Result Cache Entry validation
status: valid
example_count: 2
```

## python scripts/validate_shared_query_result_cache_contract.py
status: passed

stdout summary:
```
Shared Query/Result Cache Contract validation
status: valid
contract_file: contracts/query/search_result_cache_entry.v0.json
report_id: shared_query_result_cache_v0
example_count: 2
warnings:
- P60 is contract-only; runtime cache reads/writes remain deferred.
```

## python scripts/validate_query_observation.py --all-examples
status: passed

stdout summary:
```
Query Observation validation
status: valid
example_count: 1
```

## python scripts/validate_query_observation_contract.py
status: passed

stdout summary:
```
Query Observation Contract validation
status: valid
contract_file: contracts/query/query_observation.v0.json
report_id: query_observation_contract_v0
example_count: 1
warnings:
- P59 is contract-only; runtime query observation collection remains deferred.
```

## python scripts/validate_live_probe_gateway.py
status: passed

stdout summary:
```
Live probe gateway validation
status: valid
candidate_sources: 9
disabled_sources: 9
wrapper_live_probes_enabled: False
wrapper_live_internet_archive_enabled: False
```

## python scripts/run_hosted_public_search_rehearsal.py
status: passed

stdout summary:
```
Hosted Public Search Rehearsal
status: passed
mode: hosted_local_rehearsal
base_url: http://127.0.0.1:56954
server_started: True
checks: 60/60
safe routes: 9
safe queries: 5
blocked requests: 34/34
public index documents: 584
```

## python scripts/validate_hosted_public_search_rehearsal.py
status: passed

stdout summary:
```
Hosted Public Search Rehearsal validation
status: valid
report_id: hosted_public_search_rehearsal_v0
routes: 9
safe_queries: 5
blocked_requests: 34
live_rehearsal_status: passed
warnings:
- hosted deployment remains operator-gated/unverified.
```

## python scripts/run_public_search_safety_evidence.py
status: passed

stdout summary:
```
Public Search Safety Evidence
status: passed
mode: local_index_only
checks: 64/64
safe routes: 9
safe queries: 4
blocked requests: 32/32
public index documents: 584
```

## python scripts/validate_public_search_safety_evidence.py
status: passed

stdout summary:
```
Public Search Safety Evidence validation
status: valid
report_id: public_search_safety_evidence_v0
safe_query_count: 4
blocked_request_count: 32
```

## python scripts/validate_static_site_search_integration.py
status: passed

stdout summary:
```
Static Site Search Integration validation
status: valid
report_id: static_site_search_integration_v0
backend_status: backend_unconfigured
document_count: 584
```

## python scripts/validate_public_search_index_builder.py
status: passed

stdout summary:
```
Public Search Index Builder validation
status: valid
report_id: public_search_index_builder_v0
document_count: 584
```

## python scripts/validate_public_search_index.py
status: passed

stdout summary:
```
Public Search Index validation
status: valid
index_root: data/public_index
document_count: 584
private_paths_detected: False
```

## python scripts/validate_hosted_public_search_wrapper.py
status: passed

stdout summary:
```
Hosted public search wrapper validation
status: valid
report_id: hosted_public_search_wrapper_v0
public_search_mode: local_index_only
hosted_wrapper_implemented: True
hosted_backend_deployed: False
hosted_deployment_verified: False
```

## python scripts/check_hosted_public_search_wrapper.py
status: passed

stdout summary:
```
Hosted public search wrapper check
status: passed
mode: local_index_only
checks: 14/14
- PASS check_config: Safe defaults accepted.
- PASS healthz: OK
- PASS status_top_level: OK
- PASS status_api: OK
- PASS api_search: OK
- PASS query_plan: OK
- PASS sources: OK
- PASS html_search: OK
- PASS blocked_index_path: OK
- PASS blocked_url: OK
- PASS blocked_live_probe: OK
- PASS blocked_download: OK
- PASS blocked_upload: OK
- PASS blocked_too_long_query: OK
```

## python scripts/run_hosted_public_search.py --check-config
status: passed

stdout summary:
```
Hosted public search wrapper config
status: valid
host: 127.0.0.1
port: 8080
mode: local_index_only
hosted_deployment_verified: False
live_probes_enabled: False
downloads_enabled: False
uploads_enabled: False
local_paths_enabled: False
arbitrary_url_fetch_enabled: False
telemetry_enabled: False
```

## python scripts/validate_public_search_production_contract.py
status: passed

stdout summary:
```
Public search production contract validation
status: valid
report_id: public_search_production_contract_v0
active_mode: local_index_only
hosted_search_implemented: False
live_probes_enabled: False
```

## python scripts/validate_static_deployment_evidence.py
status: passed

stdout summary:
```
Static deployment evidence validation
status: valid
report_id: static_deployment_evidence_v0
artifact_root: site/dist
workflow_path: .github/workflows/pages.yml
deployment_verified: False
deployment_success_claimed: False
```

## python scripts/validate_post_p50_remediation.py
status: passed

stdout summary:
```
post-p50 remediation validation passed: 17 required files checked
```

## python scripts/validate_post_p49_platform_audit.py
status: passed

stdout summary:
```
post-p49 platform audit validation passed: 28 required files checked
```

## python scripts/validate_public_search_contract.py
status: passed

stdout summary:
```
Public search contract validation
status: valid
contract_id: public_search_api_contract_v0
first_allowed_mode: local_index_only
runtime_routes_implemented: True
registered_routes: 6
forbidden_parameters: 26
```

## python scripts/validate_public_search_result_card_contract.py
status: passed

stdout summary:
```
status: valid
contract_id: public_search_result_card_contract_v0
schema: contracts/api/search_result_card.v0.json
response_schema: contracts/api/search_response.v0.json
audit_pack: control/audits/public-search-result-card-contract-v0
examples: 5
```

## python scripts/validate_public_search_safety.py
status: passed

stdout summary:
```
Public Search Safety / Abuse Guard validation
status: valid
safety_policy_id: eureka-public-search-safety-abuse-guard-v0
first_allowed_mode: local_index_only
max_query_length: 160
max_result_limit: 25
max_runtime_ms_contract: 3000
telemetry_default: off
```

## python scripts/validate_local_public_search_runtime.py
status: passed

stdout summary:
```
Local Public Search Runtime validation
status: valid
runtime_scope: local_prototype_backend
mode: local_index_only
routes: 6
hosted_public_deployment: False
static_search_handoff: True
```

## python scripts/public_search_smoke.py
status: passed

stdout summary:
```
Public Search Smoke
status: passed
mode: local_index_only
checks: 30/30 passed
safe queries: 9
blocked requests: 14

[PASS] status: /api/v1/status (ok)
[PASS] search: /api/v1/search?q=windows+7+apps (ok)
[PASS] driver search: /api/v1/search?q=driver.inf (ok)
[PASS] query plan: /api/v1/query-plan?q=windows+7+apps (ok)
[PASS] sources: /api/v1/sources (ok)
[PASS] source detail: /api/v1/source/synthetic-fixtures (ok)
[PASS] html search: /search?q=windows+7+apps (ok)
[PASS] safe query: windows 7 apps: /api/v1/search?q=windows+7+apps (ok)
[PASS] safe query: latest firefox before xp support ended: /api/v1/search?q=latest+firefox+before+xp+support+ended (ok)
[PASS] safe query: driver.inf: /api/v1/search?q=driver.inf (ok)
[PASS] safe query: thinkpad t42 wifi windows 2000: /api/v1/search?q=thinkpad+t42+wifi+windows+2000 (ok)
[PASS] safe query: registry repair: /api/v1/search?q=registry+repair (ok)
[PASS] safe query: blue ftp: /api/v1/search?q=blue+ftp (ok)
```

## python scripts/public_search_smoke.py --json
status: passed

stdout summary:
```
{
  "base_runtime_slice": "local_public_search_runtime_v0",
  "blocked_request_results": [
    {
      "actual_error_code": "query_required",
      "expected_error_code": "query_required",
      "message": "Check passed.",
      "name": "missing q",
      "no_private_path_leakage": true,
      "no_stack_trace": true,
      "observed_status": 400,
      "ok": false,
      "passed": true,
      "route": "/api/v1/search"
    },
    {
      "actual_error_code": "query_too_long",
      "expected_error_code": "query_too_long",
      "message": "Check passed.",
      "name": "query too long",
```

## python scripts/build_public_search_index.py --check
status: passed

stdout summary:
```
Public Search Index Builder v0
status: valid
output_root: data/public_index
document_count: 584
fts5_available: True
fts5_enabled: False
fallback_enabled: True
```

## python site/build.py --check
status: passed

stdout summary:
```
Static site generator
status: valid
source_root: site
deploy_artifact_current: site/dist
```

## python site/validate.py
status: passed

stdout summary:
```
Static site generator validation
status: valid
page_count: 9
dist_validation: valid
```

## python scripts/validate_publication_inventory.py
status: passed

stdout summary:
```
Publication inventory validation
status: valid
registered_routes: 51
current_static_artifact_pages: 9
required_client_profiles: 9
required_public_data_paths: 14
```

## python scripts/validate_public_static_site.py
status: passed

stdout summary:
```
Public static site validation
status: valid
pages: 9
source_ids_checked: 15
```

## python scripts/check_github_pages_static_artifact.py --path site/dist
status: passed

stdout summary:
```
GitHub Pages static artifact check
status: valid
site_dir: [local-path]
static_site_validator: valid
publication_inventory_validator: valid
```

## python scripts/check_generated_artifact_drift.py
status: passed

stdout summary:
```
Generated Artifact Drift Guard v0
status: valid
inventory: control/inventory/generated_artifacts/generated_artifacts.json
policy: control/inventory/generated_artifacts/drift_policy.json
strict: False
status_counts: {'passed': 12}
- public_data_summaries: passed
  - check_command: passed (python scripts/generate_public_data_summaries.py --check)
  - validator_command: passed (python scripts/validate_public_static_site.py)
  - validator_command: passed (python scripts/validate_public_data_stability.py)
- compatibility_surfaces: passed
  - check_command: passed (python scripts/generate_compatibility_surfaces.py --check)
  - validator_command: passed (python scripts/validate_compatibility_surfaces.py)
- static_resolver_demos: passed
  - check_command: passed (python scripts/generate_static_resolver_demos.py --check)
  - validator_command: passed (python scripts/validate_public_static_site.py)
- static_snapshot_example: passed
  - check_command: passed (python scripts/generate_static_snapshot.py --check)
  - validator_command: passed (python scripts/validate_static_snapshot.py)
  - validator_command: passed (python scripts/validate_snapshot_consumer_contract.py)
```

## python scripts/public_alpha_smoke.py
status: passed

stdout summary:
```
Public Alpha Smoke
status: passed
mode: public_alpha
checks: 18/18 passed

[PASS] status: /api/status (ok)
[PASS] source list: /api/sources (ok)
[PASS] query plan: /api/query-plan?q=Windows+7+apps (ok)
[PASS] search: /api/search?q=synthetic (ok)
[PASS] public search status: /api/v1/status (ok)
[PASS] public search: /api/v1/search?q=windows+7+apps (ok)
[PASS] public query plan: /api/v1/query-plan?q=windows+7+apps (ok)
[PASS] archive resolution evals: /api/evals/archive-resolution (ok)
[PASS] local index path: /api/index/status?index_path=D%3A%2Fprivate%2Feureka-index.sqlite3 (local_path_parameters_blocked)
[PASS] run store root: /api/runs?run_store_root=D%3A%2Fprivate%2Feureka-runs (local_path_parameters_blocked)
[PASS] task store root: /api/tasks?task_store_root=D%3A%2Fprivate%2Feureka-tasks (local_path_parameters_blocked)
[PASS] memory store root: /api/memories?memory_store_root=D%3A%2Fprivate%2Feureka-memory (local_path_parameters_blocked)
[PASS] bundle path inspection: /api/inspect/bundle?bundle_path=D%3A%2Fprivate%2Feureka-bundle.zip (local_path_parameters_blocked)
[PASS] stored export root: /api/stored?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0&store_root=D%3A%2Fprivate%2Feureka-store (local_path_parameters_blocked)
[PASS] arbitrary output path: /api/status?output=D%3A%2Fprivate%2Foutput.json (local_path_parameters_blocked)
```

## python scripts/run_archive_resolution_evals.py
status: passed

stdout summary:
```
Archive resolution evals
created_by_slice: archive_resolution_eval_runner_v0
task_count: 6
status_counts: satisfied=6

Tasks
- article_inside_magazine_scan: satisfied (planner=satisfied, search=local_index, results=9)
- driver_inside_support_cd: satisfied (planner=satisfied, search=local_index, results=50)
- latest_firefox_before_xp_drop: satisfied (planner=satisfied, search=local_index, results=50)
- old_blue_ftp_client_xp: satisfied (planner=satisfied, search=local_index, results=44)
- win98_registry_repair: satisfied (planner=satisfied, search=local_index, results=26)
- windows_7_apps: satisfied (planner=satisfied, search=local_index, results=29)
```

## python scripts/run_archive_resolution_evals.py --json
status: passed

stdout summary:
```
{
  "created_at": "2026-05-05T09:14:27.530146+00:00",
  "created_by_slice": "archive_resolution_eval_runner_v0",
  "load_errors": [],
  "notices": [
    {
      "code": "transient_local_index",
      "message": "Built a transient Local Index v0 database for this eval run. The report omits the temporary path so JSON remains inspectable.",
      "severity": "info"
    },
    {
      "code": "local_index_built_for_eval",
      "message": "Built Local Index v0 once for this synchronous archive-resolution eval suite.",
      "severity": "info"
    }
  ],
  "status_counts": {
    "satisfied": 6
  },
  "task_summaries": [
```

## python scripts/run_search_usefulness_audit.py
status: passed

stdout summary:
```
Search usefulness audit
created_by_slice: search_usefulness_audit_v0
query_count: 64
eureka_status_counts: capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2
external_pending_counts: google=64, internet_archive_full_text=64, internet_archive_metadata=64
failure_mode_counts: absence_reasoning_gap=2, actionability_gap=2, compatibility_evidence_gap=25, decomposition_gap=12, external_baseline_pending=64, identity_cluster_gap=14, index_gap=2, live_source_gap=10, member_access_gap=12, planner_gap=24, query_interpretation_gap=21, ranking_gap=9, representation_gap=14, source_coverage_gap=49, surface_ux_gap=4

Top future-work recommendations
- source_coverage_gap: 49 (Add governed source coverage or recorded fixtures for the observed query family.)
- compatibility_evidence_gap: 25 (Add source-backed compatibility clues and host-profile evidence.)
- planner_gap: 24 (Teach deterministic Query Planner v0 another bounded query family.)
- query_interpretation_gap: 21 (Capture missing structured intent or constraints in the planner.)
- representation_gap: 14 (Add representation/access-path metadata for actionable units.)
- identity_cluster_gap: 14 (Group ambiguous names, versions, and source-backed states without merging truth.)
- decomposition_gap: 12 (Represent container/member-level evidence for packages, ISOs, scans, or support media.)
- member_access_gap: 12 (Expose useful member previews/readback where bounded local fixtures support it.)
- live_source_gap: 10 (Design a governed live-source strategy later; no live crawling is part of this audit.)
- ranking_gap: 9 (Future ranking work may be needed; this audit does not implement ranking.)

Queries
```

## python scripts/run_search_usefulness_audit.py --json
status: passed

stdout summary:
```
{
  "created_at": "2026-05-05T09:14:28.282732+00:00",
  "created_by_slice": "search_usefulness_audit_v0",
  "eureka_status_counts": {
    "capability_gap": 7,
    "covered": 5,
    "partial": 40,
    "source_gap": 10,
    "unknown": 2
  },
  "external_baseline_pending_counts": {
    "google": 64,
    "internet_archive_full_text": 64,
    "internet_archive_metadata": 64
  },
  "failure_mode_counts": {
    "absence_reasoning_gap": 2,
    "actionability_gap": 2,
    "compatibility_evidence_gap": 25,
    "decomposition_gap": 12,
```

## python scripts/report_external_baseline_status.py --json
status: passed

stdout summary:
```
{
  "batches": {
    "batch_0": {
      "completion_percent": 0.0,
      "directory": "[local-path],
      "expected_observation_count": 39,
      "missing_observation_slots": [],
      "next_pending_slots": [
        {
          "batch_id": "batch_0",
          "observation_id": "batch_0::windows_7_apps::google_web_search",
          "observation_status": "pending_manual_observation",
          "query_id": "windows_7_apps",
          "query_text": "Windows 7 apps",
          "system_id": "google_web_search"
        },
        {
          "batch_id": "batch_0",
          "observation_id": "batch_0::windows_7_apps::internet_archive_metadata_search",
          "observation_status": "pending_manual_observation",
```

## python scripts/generate_python_oracle_golden.py --check
status: passed

stdout summary:
```
Python oracle golden fixture pack
status: passed
fixture_pack_id: python_oracle_golden_v0
fixture_pack_version: 0.1.0
output_root: [local-path]
file_count: 40
```

## python -m unittest discover -s tests/scripts -t .
status: passed

stderr summary:
```
.................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 465 tests in 107.901s

OK
```

## python -m unittest discover -s tests/operations -t .
status: passed

stderr summary:
```
....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 516 tests in 8.445s

OK
```

## python -m unittest discover -s tests/hardening -t .
status: passed

stderr summary:
```
.....................................................
----------------------------------------------------------------------
Ran 53 tests in 5.207s

OK
```

## python -m unittest discover -s tests/parity -t .
status: passed

stderr summary:
```
.........................
----------------------------------------------------------------------
Ran 25 tests in 1.380s

OK
```

## python -m unittest discover -s runtime -t .
status: passed

stderr summary:
```
................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 320 tests in 4.810s

OK
```

## python -m unittest discover -s surfaces -t .
status: passed

stderr summary:
```
........................................................................................................................................................................
----------------------------------------------------------------------
Ran 168 tests in 29.989s

OK
```

## python -m unittest discover -s tests -t .
status: passed

stderr summary:
```
..............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 1150 tests in 119.866s

OK
```

## python scripts/check_architecture_boundaries.py
status: passed

stdout summary:
```
Checked 446 Python files under [local-path]
No architecture-boundary violations found.
```

## git diff --check
status: passed

stderr summary:
```
warning: in the working copy of 'site/dist/assets/site.css', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/README.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/absence-example.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/comparison-example.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/data/demo_snapshots.json', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/eval-summary.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/index.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/query-plan-windows-7-apps.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/result-article-scan.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/result-firefox-xp.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/result-member-driver-inside-support-cd.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/demo/source-example.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/README.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/SHA256SUMS', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/data/README.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/index.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/index.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/manifest.json', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/files/search.README.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/lite/README.txt', LF will be replaced by CRLF the next time Git touches it
```

## git status --short --branch
status: passed

stdout summary:
```
## main...origin/main
 M .aide/commands/ci.yaml
 M .aide/commands/dev.yaml
 M .aide/reports/README.md
 M .aide/tasks/audit_backlog.yaml
 M .aide/tasks/queue.yaml
 M contracts/connectors/README.md
 M control/audits/README.md
 M control/inventory/sources/package-registry-recorded-fixtures.source.json
 M control/inventory/tests/command_matrix.json
 M control/inventory/tests/test_registry.json
 M docs/BOOTSTRAP_STATUS.md
 M docs/DECISIONS.md
 M docs/OPEN_QUESTIONS.md
 M docs/ROADMAP.md
 M docs/architecture/SOURCE_INGESTION_PLANE.md
 M docs/operations/HOSTED_PUBLIC_SEARCH_REHEARSAL.md
 M docs/operations/LIVE_PROBE_POLICY.md
 M docs/operations/PUBLIC_SEARCH_SAFETY_EVIDENCE.md
 M docs/reference/CANDIDATE_INDEX_CONTRACT.md
```

## cargo --version
status: skipped
reason: cargo unavailable

## cargo check --workspace --manifest-path crates/Cargo.toml
status: skipped
reason: cargo unavailable

## cargo test --workspace --manifest-path crates/Cargo.toml
status: skipped
reason: cargo unavailable
