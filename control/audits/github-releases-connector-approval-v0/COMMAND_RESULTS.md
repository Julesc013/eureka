# Command Results

## python scripts/validate_github_releases_connector_approval.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 1
```

## python scripts/validate_github_releases_connector_approval.py --all-examples --json

status: passed
returncode: 0
```text
{
  "status": "valid",
  "created_by": "github_releases_connector_approval_validator_v0",
  "example_count": 1,
  "results": [
    {
      "status": "valid",
      "created_by": "github_releases_connector_approval_validator_v0",
      "approval": "examples\\connectors\\github_releases_approval_v0\\GITHUB_RELEASES_CONNECTOR_APPROVAL.json",
      "approval_record_id": "example.connector.github_releases.approval.v0",
      "errors": [],
      "warnings": [],
      "approval_root": "examples\\connectors\\github_releases_approval_v0"
    }
  ],
  "errors": [],
  "warnings": []
}
```

## python scripts/validate_github_releases_connector_contract.py

status: passed
returncode: 0
```text
status: valid
example_count: 1
contract_file: contracts/connectors/github_releases_connector_approval.v0.json
```

## python scripts/validate_github_releases_connector_contract.py --json

status: passed
returncode: 0
```text
{
  "status": "valid",
  "created_by": "github_releases_connector_contract_validator_v0",
  "contract_file": "contracts/connectors/github_releases_connector_approval.v0.json",
  "example_count": 1,
  "errors": [],
  "warnings": []
}
```

## python scripts/dry_run_github_releases_connector_approval.py --json

status: passed
returncode: 0
```text
{
  "schema_version": "0.1.0",
  "approval_record_id": "dry_run.connector.github_releases.approval.v0",
  "approval_record_kind": "github_releases_connector_approval",
  "status": "draft_example",
  "created_by_tool": "dry_run_github_releases_connector_approval_v0",
  "connector_ref": {
    "connector_id": "github_releases_connector",
    "connector_label": "GitHub Releases metadata connector",
    "source_family": "github_releases",
    "connector_version": "dry-run",
    "source_inventory_ref": "control/inventory/sources/github-releases-recorded-fixtures.source.json",
    "source_status": "approval_required",
    "limitations": [
      "Dry-run only; no live connector execution."
    ]
  },
  "approval_checklist_status": "pending",
  "operator_checklist_status": "pending",
  "repository_identity_review_required": true,
  "source_policy_review_required": true,
  "token_policy_review_required": true,
  "user_agent_contact_required_future": true,
  "rate_limit_required_future": true,
  "timeout_required_future": true,
  "retry_backoff_required_future": true,
  "circuit_breaker_required_future": true,
  "cache_first_required": true,
  "connector_runtime_implemented": false,
  "connector_approved_now": false,
  "live_source_called": false,
  "external_calls_performed": false,
  "github_api_called": false,
  "repository_cloned": false,
  "releases_fetched": false,
  "release_assets_downloaded": false,
  "source_archive_downloaded": false,
  "public_search_live_fanout_enabled": false,
  "arbitrary_repository_fetch_allowed": false,
  "source_cache_mutated": false,
  "evidence_ledger_mutated": false,
  "candidate_index_mutated": false,
  "public_index_mutated": false,
  "local_index_mutated": false,
  "master_index_mutated": false,
  "downloads_enabled": false,
  "file_retrieval_enabled": false,
  "mirroring_enabled": false,
  "installs_enabled": false,
  "execution_enabled": false,
  "credentials_used": false,
  "github_token_used": false,
  "telemetry_exported": false,
  "notes": [
    "Stdout-only dry run. No files are written, no network is used, and no connector/source/cache/ledger/index runtime is called."
  ]
}
```

## python scripts/validate_wayback_cdx_memento_connector_approval.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 1
```

## python scripts/validate_wayback_cdx_memento_connector_contract.py

status: passed
returncode: 0
```text
status: valid
example_count: 1
contract_file: contracts/connectors/wayback_cdx_memento_connector_approval.v0.json
```

## python scripts/validate_internet_archive_metadata_connector_approval.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 1
```

## python scripts/validate_internet_archive_metadata_connector_contract.py

status: passed
returncode: 0
```text
status: valid
example_count: 1
contract_file: contracts/connectors/internet_archive_metadata_connector_approval.v0.json
```

## python scripts/validate_source_cache_record.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 3
```

## python scripts/validate_source_cache_contract.py

status: passed
returncode: 0
```text
status: valid
example_count: 3
contract_file: contracts/source_cache/source_cache_record.v0.json
```

## python scripts/validate_evidence_ledger_record.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 3
```

## python scripts/validate_evidence_ledger_contract.py

status: passed
returncode: 0
```text
status: valid
example_count: 3
contract_file: contracts/evidence_ledger/evidence_ledger_record.v0.json
```

## python scripts/validate_source_cache_evidence_ledger_contract.py

status: passed
returncode: 0
```text
status: valid
report_id: source_cache_evidence_ledger_v0
```

## python scripts/validate_source_sync_worker_job.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 4
```

## python scripts/validate_source_sync_worker_contract.py

status: passed
returncode: 0
```text
status: valid
contract_file: contracts/source_sync/source_sync_worker_job.v0.json
example_count: 4
```

## python scripts/validate_demand_dashboard_snapshot.py --all-examples

status: passed
returncode: 0
```text
status: valid
example_count: 2
```

## python scripts/validate_demand_dashboard_contract.py

status: passed
returncode: 0
```text
status: valid
contract_file: contracts/query/demand_dashboard_snapshot.v0.json
example_count: 2
```

## python scripts/validate_query_guard_decision.py --all-examples

status: passed
returncode: 0
```text
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
returncode: 0
```text
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
returncode: 0
```text
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
returncode: 0
```text
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
returncode: 0
```text
Candidate Promotion Assessment validation
status: valid
example_count: 4
```

## python scripts/validate_candidate_promotion_policy.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Candidate Index Record validation
status: valid
example_count: 4
```

## python scripts/validate_candidate_index_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Probe Queue Item validation
status: valid
example_count: 3
```

## python scripts/validate_probe_queue_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Search Need Record validation
status: valid
example_count: 2
```

## python scripts/validate_search_need_record_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Search Miss Ledger Entry validation
status: valid
example_count: 2
```

## python scripts/validate_search_miss_ledger_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Search Result Cache Entry validation
status: valid
example_count: 2
```

## python scripts/validate_shared_query_result_cache_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Query Observation validation
status: valid
example_count: 1
```

## python scripts/validate_query_observation_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
Live probe gateway validation
status: valid
candidate_sources: 9
disabled_sources: 9
wrapper_live_probes_enabled: False
wrapper_live_internet_archive_enabled: False
```

## python scripts/run_hosted_public_search_rehearsal.py

status: passed
returncode: 0
```text
Hosted Public Search Rehearsal
status: passed
mode: hosted_local_rehearsal
base_url: http://127.0.0.1:55591
server_started: True
checks: 60/60
safe routes: 9
safe queries: 5
blocked requests: 34/34
public index documents: 584
```

## python scripts/validate_hosted_public_search_rehearsal.py

status: passed
returncode: 0
```text
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
returncode: 0
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

## python scripts/validate_public_search_safety_evidence.py

status: passed
returncode: 0
```text
Public Search Safety Evidence validation
status: valid
report_id: public_search_safety_evidence_v0
safe_query_count: 4
blocked_request_count: 32
```

## python scripts/validate_static_site_search_integration.py

status: passed
returncode: 0
```text
Static Site Search Integration validation
status: valid
report_id: static_site_search_integration_v0
backend_status: backend_unconfigured
document_count: 584
```

## python scripts/validate_public_search_index_builder.py

status: passed
returncode: 0
```text
Public Search Index Builder validation
status: valid
report_id: public_search_index_builder_v0
document_count: 584
```

## python scripts/validate_public_search_index.py

status: passed
returncode: 0
```text
Public Search Index validation
status: valid
index_root: data/public_index
document_count: 584
private_paths_detected: False
```

## python scripts/validate_hosted_public_search_wrapper.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
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
returncode: 0
```text
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
returncode: 0
```text
Public search production contract validation
status: valid
report_id: public_search_production_contract_v0
active_mode: local_index_only
hosted_search_implemented: False
live_probes_enabled: False
```

## python scripts/validate_static_deployment_evidence.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
post-p50 remediation validation passed: 17 required files checked
```

## python scripts/validate_post_p49_platform_audit.py

status: passed
returncode: 0
```text
post-p49 platform audit validation passed: 28 required files checked
```

## python scripts/validate_public_search_contract.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
status: valid
contract_id: public_search_result_card_contract_v0
schema: contracts/api/search_result_card.v0.json
response_schema: contracts/api/search_response.v0.json
audit_pack: control/audits/public-search-result-card-contract-v0
examples: 5
```

## python scripts/validate_public_search_safety.py

status: passed
returncode: 0
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

## python scripts/validate_local_public_search_runtime.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
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
[PASS] safe query: pc magazine ray tracing: /api/v1/search?q=pc+magazine+ray+tracing (ok)
[PASS] safe query: archive: /api/v1/search?q=archive (ok)
[PASS] safe query: no-such-local-index-hit: /api/v1/search?q=no-such-local-index-hit (ok)
[PASS] blocked request: missing q: /api/v1/search (query_required)
[PASS] blocked request: query too long: /api/v1/search?q=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (query_too_long)
[PASS] blocked request: limit too large: /api/v1/search?q=windows&limit=26 (limit_too_large)
[PASS] blocked request: unsupported mode live_probe: /api/v1/search?q=windows&mode=live_probe (live_probes_disabled)
[PASS] blocked request: forbidden index_path: /api/v1/search?q=windows&index_path=blocked-local-index (local_paths_forbidden)
[PASS] blocked request: forbidden store_root: /api/v1/search?q=windows&store_root=blocked-store-root (local_paths_forbidden)
[PASS] blocked request: forbidden url: /api/v1/search?q=windows&url=https%3A%2F%2Fexample.invalid%2F (forbidden_parameter)
[PASS] blocked request: forbidden fetch_url: /api/v1/search?q=windows&fetch_url=https%3A%2F%2Fexample.invalid%2F (forbidden_parameter)
[PASS] blocked request: download disabled: /api/v1/search?q=windows&download=true (downloads_disabled)
[PASS] blocked request: install disabled: /api/v1/search?q=windows&install=true (installs_disabled)
[PASS] blocked request: upload disabled: /api/v1/search?q=windows&upload=true (uploads_disabled)
[PASS] blocked request: source credentials forbidden: /api/v1/search?q=windows&source_credentials=redacted (forbidden_parameter)
[PASS] blocked request: api key forbidden: /api/v1/search?q=windows&api-key-redacted (forbidden_parameter)
[PASS] blocked request: live source disabled: /api/v1/search?q=windows&live_source=internet_archive (live_probes_disabled)
```

## python scripts/public_search_smoke.py --json

status: passed
returncode: 0
```text
"observed_status": 200,
      "passed": true,
      "route": "/search?q=windows+7+apps"
    }
  ],
  "safe_query_results": [
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "windows 7 apps",
      "result_cards_contract_ok": true,
      "result_count": 10,
      "route": "/api/v1/search?q=windows+7+apps",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "latest firefox before xp support ended",
      "result_cards_contract_ok": true,
      "result_count": 0,
      "route": "/api/v1/search?q=latest+firefox+before+xp+support+ended",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "driver.inf",
      "result_cards_contract_ok": true,
      "result_count": 10,
      "route": "/api/v1/search?q=driver.inf",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "thinkpad t42 wifi windows 2000",
      "result_cards_contract_ok": true,
      "result_count": 10,
      "route": "/api/v1/search?q=thinkpad+t42+wifi+windows+2000",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "registry repair",
      "result_cards_contract_ok": true,
      "result_count": 10,
      "route": "/api/v1/search?q=registry+repair",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "blue ftp",
      "result_cards_contract_ok": true,
      "result_count": 10,
      "route": "/api/v1/search?q=blue+ftp",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "pc magazine ray tracing",
      "result_cards_contract_ok": true,
      "result_count": 9,
      "route": "/api/v1/search?q=pc+magazine+ray+tracing",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "archive",
      "result_cards_contract_ok": true,
      "result_count": 10,
      "route": "/api/v1/search?q=archive",
      "warnings_present": true
    },
    {
      "envelope_ok": true,
      "limitations_or_absence_present": true,
      "message": "Check passed.",
      "no_private_path_leakage": true,
      "observed_status": 200,
      "ok": true,
      "passed": true,
      "query": "no-such-local-index-hit",
      "result_cards_contract_ok": true,
      "result_count": 0,
      "route": "/api/v1/search?q=no-such-local-index-hit",
      "warnings_present": true
    }
  ],
  "status": "passed",
  "telemetry_enabled": false,
  "total_checks": 30,
  "uploads_enabled": false
}
```

## python scripts/build_public_search_index.py --check

status: passed
returncode: 0
```text
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
returncode: 0
```text
Static site generator
status: valid
source_root: site
deploy_artifact_current: site/dist
```

## python site/validate.py

status: passed
returncode: 0
```text
Static site generator validation
status: valid
page_count: 9
dist_validation: valid
```

## python scripts/validate_publication_inventory.py

status: passed
returncode: 0
```text
Publication inventory validation
status: valid
registered_routes: 51
current_static_artifact_pages: 9
required_client_profiles: 9
required_public_data_paths: 14
```

## python scripts/validate_public_static_site.py

status: passed
returncode: 0
```text
Public static site validation
status: valid
pages: 9
source_ids_checked: 15
```

## python scripts/check_github_pages_static_artifact.py --path site/dist

status: passed
returncode: 0
```text
GitHub Pages static artifact check
status: valid
site_dir:  <repo> \site\dist
static_site_validator: valid
publication_inventory_validator: valid
```

## python scripts/check_generated_artifact_drift.py

status: passed
returncode: 0
```text
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
- static_site_dist: passed
  - check_command: passed (python site/build.py --check)
  - validator_command: passed (python site/validate.py)
  - validator_command: passed (python scripts/check_github_pages_static_artifact.py --path site/dist)
  - validator_command: passed (python scripts/validate_public_search_static_handoff.py)
- python_oracle_goldens: passed
  - check_command: passed (python scripts/generate_python_oracle_golden.py --check)
  - validator_command: passed (python -m unittest tests.hardening.test_python_oracle_golden_guard)
- public_alpha_rehearsal_evidence: passed
  - check_command: passed (python scripts/generate_public_alpha_rehearsal_evidence.py --check)
  - validator_command: passed (python scripts/public_alpha_smoke.py)
- publication_inventory: passed
  - check_command: passed (python scripts/validate_publication_inventory.py)
  - validator_command: passed (python scripts/validate_publication_inventory.py --json)
  - validator_command: passed (python scripts/validate_public_static_site.py)
- test_registry: passed
  - check_command: passed (python -m unittest tests.operations.test_test_eval_operating_layer)
  - validator_command: passed (python -m unittest tests.hardening.test_aide_test_registry_consistency)
- aide_metadata: passed
  - check_command: passed (python -m unittest tests.hardening.test_aide_test_registry_consistency)
  - validator_command: passed (python -m unittest tests.operations.test_test_eval_operating_layer)
- public_search_index: passed
  - check_command: passed (python scripts/build_public_search_index.py --check)
  - validator_command: passed (python scripts/validate_public_search_index.py)
  - validator_command: passed (python scripts/validate_public_search_index_builder.py)
- static_search_integration: passed
  - check_command: passed (python site/build.py --check)
  - validator_command: passed (python scripts/validate_static_site_search_integration.py)
  - validator_command: passed (python scripts/validate_public_static_site.py)
errors: []
```

## python scripts/public_alpha_smoke.py

status: passed
returncode: 0
```text
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
[PASS] fixture byte fetch: /api/fetch?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0&representation_id=rep.synthetic-demo-app.source (route_disabled_in_public_alpha)
[PASS] public search arbitrary url: /api/v1/search?q=archive&url=https%3A%2F%2Fexample.invalid%2F (forbidden_parameter)
[PASS] public search live probe: /api/v1/search?q=archive&live_probe=1 (live_probes_disabled)
```

## python scripts/run_archive_resolution_evals.py

status: passed
returncode: 0
```text
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
returncode: 0
```text
e_pack_v0",
              "evidence_id": "compat-evidence:sha256:b8e4260bdf529b2752f04d162d28e5a6fc917948b143d0bf47eac0b50f06dbb3",
              "evidence_kind": "file_path",
              "evidence_text": "portable-app-package/README-windows7.txt",
              "locator": "runtime/connectors/internet_archive_recorded/fixtures/internet_archive_items_fixture.json#ia-win7-portable-apps-fixture/files/0",
              "platform": {
                "family": "windows",
                "marketing_alias": "Windows 7",
                "name": "Windows 7",
                "version": "NT 6.1"
              },
              "source_family": "internet_archive_recorded",
              "source_id": "internet-archive-recorded-fixtures",
              "source_label": "Internet Archive Recorded Fixtures",
              "subject_resolved_resource_id": "obj.internet-archive-recorded.ia.win7.portable.apps.fixture",
              "subject_target_ref": "internet-archive-recorded:ia-win7-portable-apps-fixture"
            }
          ],
          "compatibility_summary": "Windows 7: supports_platform via compatibility_note (medium); Windows 7: supports_platform via source_metadata (medium); Windows 7: mentions_platform via source_metadata (medium); +1 more",
          "evidence": [
            "label Windows 7 portable apps archive recorded fixture internet_archive_recorded source_metadata Internet Archive Recorded Fixtures",
            "source_identifier ia-win7-portable-apps-fixture internet_archive_recorded source_metadata Internet Archive Recorded Fixtures",
            "description Recorded metadata for Windows 7 apps and Windows NT 6.1 utilities. The file list uses text stand-ins for an individual application installer and portable app package with Windows 7 compatibility evidence. internet_archive_recorded source_metadata Internet Archive Recorded Fixtures",
            "compatibility_note Windows 7; Windows NT 6.1; x86; x64; portable_app_package; individual_application_installer; compatibility_note internet_archive_recorded source_metadata Internet Archive Recorded Fixtures",
            "file_listing portable-app-package/README-windows7.txt internet_archive_recorded file_listing Internet Archive Recorded Fixtures",
            "file_listing portable-app-package/individual-application-installer.exe.txt internet_archive_recorded file_listing Internet Archive Recorded Fixtures"
          ],
          "index_record_id": "resolved_object:internet-archive-recorded:ia-win7-portable-apps-fixture",
          "label": "Windows 7 portable apps archive recorded fixture",
          "primary_lane": "preservation",
          "record_kind": "resolved_object",
          "representation_id": "rep.internet-archive-recorded.ia.win7.portable.apps.fixture.metadata",
          "resolved_resource_id": "obj.internet-archive-recorded.ia.win7.portable.apps.fixture",
          "result_lanes": [
            "preservation"
          ],
          "route_hints": {
            "record_kind": "resolved_object",
            "surface_route": "/",
            "target_ref": "internet-archive-recorded:ia-win7-portable-apps-fixture"
          },
          "source_family": "internet_archive_recorded",
          "source_id": "internet-archive-recorded-fixtures",
          "source_label": "Internet Archive Recorded Fixtures",
          "subject_key": "obj.internet-archive-recorded.ia.win7.portable.apps.fixture",
          "summary": "software from Internet Archive Recorded Fixtures",
          "target_ref": "internet-archive-recorded:ia-win7-portable-apps-fixture",
          "usefulness_summary": "preservation; user cost 3; why: preservation_source; source_evidence_present",
          "user_cost_reasons": [
            "preservation_source",
            "source_evidence_present"
          ],
          "user_cost_score": 3,
          "version_or_state": "state.internet-archive-recorded.ia.win7.portable.apps.fixture.recorded"
        }
      ]
    }
  ],
  "total_task_count": 6
}
```

## python scripts/run_search_usefulness_audit.py

status: passed
returncode: 0
```text
se, search=local_index, results=9)
- latest_firefox_before_xp_support_ended: partial (family=latest_compatible_release, search=local_index, results=42)
- latest_vlc_for_windows_xp: partial (family=latest_compatible_release, search=local_index, results=9)
- local_index_archive_query: partial (family=current_covered_sanity, search=local_index, results=50)
- mac_os_9_browser: partial (family=platform_software, search=local_index, results=9)
- macworld_system_7_review: source_gap (family=article_inside_scan, search=local_index, results=0)
- manual_sound_blaster_ct1740: partial (family=manual_documentation, search=local_index, results=6)
- missing_subject_query: capability_gap (family=negative_absence, search=local_index, results=0)
- missing_synthetic_target_absence: capability_gap (family=negative_absence, search=local_index, results=0)
- nonsensical_vintage_software_query: unknown (family=negative_absence, search=local_index, results=0)
- old_blue_ftp_client_xp: partial (family=vague_identity, search=local_index, results=29)
- old_creative_labs_driver_page: partial (family=web_archive_dead_link, search=local_index, results=6)
- old_ftp_client_blue_icon_windows_xp: partial (family=vague_identity, search=local_index, results=3)
- old_mac_compression_utility: source_gap (family=vague_identity, search=local_index, results=0)
- old_netscape_download_page: partial (family=web_archive_dead_link, search=local_index, results=6)
- package_release_with_source_tarball: partial (family=source_code_package_release, search=local_index, results=6)
- pc_magazine_july_1994_ray_tracing: partial (family=article_inside_scan, search=local_index, results=9)
- powerpc_osx_104_browser: partial (family=platform_software, search=local_index, results=9)
- public_alpha_status_query: capability_gap (family=current_covered_sanity, search=local_index, results=0)
- query_planner_windows_7_apps: partial (family=current_covered_sanity, search=local_index, results=11)
- readme_inside_old_zip: partial (family=package_container_member, search=local_index, results=1)
- software_heritage_snapshot_old_project: partial (family=source_code_package_release, search=local_index, results=6)
- sound_blaster_live_ct4830_driver_windows_98: source_gap (family=driver_hardware_support, search=local_index, results=0)
- sound_blaster_live_manual: partial (family=manual_documentation, search=local_index, results=5)
- source_registry_synthetic_fixtures: covered (family=current_covered_sanity, search=local_index, results=4)
- support_cd_member_driver: partial (family=package_container_member, search=local_index, results=10)
- synthetic_demo_app_exact: covered (family=current_covered_sanity, search=local_index, results=10)
- synthetic_package_member_readme: covered (family=current_covered_sanity, search=local_index, results=2)
- thinkpad_t42_hardware_maintenance_manual: partial (family=manual_documentation, search=local_index, results=5)
- threecom_3c905_windows_95_driver: partial (family=driver_hardware_support, search=local_index, results=20)
- unsupported_platform_query: unknown (family=negative_absence, search=local_index, results=0)
- visual_cpp_6_service_pack_download: partial (family=package_container_member, search=local_index, results=2)
- visual_cpp_6_sp_readme: partial (family=manual_documentation, search=local_index, results=4)
- windows_2000_antivirus: partial (family=platform_software, search=local_index, results=6)
- windows_7_apps: partial (family=platform_software, search=local_index, results=11)
- windows_7_portable_apps_archive: partial (family=platform_software, search=local_index, results=11)
- windows_98_registry_repair: partial (family=platform_software, search=local_index, results=28)
- windows_98_resource_kit_pdf: partial (family=manual_documentation, search=local_index, results=6)
- windows_xp_ftp_clients: partial (family=platform_software, search=local_index, results=31)
- windows_xp_software: partial (family=platform_software, search=local_index, results=21)
```

## python scripts/run_search_usefulness_audit.py --json

status: passed
returncode: 0
```text
2000_antivirus",
      "search_mode": "local_index",
      "search_result_count": 6
    },
    {
      "eureka_status": "partial",
      "expected_eureka_current_status": "source_gap",
      "failure_modes": [
        "source_coverage_gap",
        "compatibility_evidence_gap",
        "ranking_gap",
        "external_baseline_pending"
      ],
      "future_work_labels": [
        "source_coverage_gap",
        "compatibility_evidence_gap",
        "ranking_gap"
      ],
      "planner_observed_task_kind": "browse_software",
      "query": "Windows 7 apps",
      "query_family": "platform_software",
      "query_id": "windows_7_apps",
      "search_mode": "local_index",
      "search_result_count": 11
    },
    {
      "eureka_status": "partial",
      "expected_eureka_current_status": "source_gap",
      "failure_modes": [
        "source_coverage_gap",
        "decomposition_gap",
        "compatibility_evidence_gap",
        "external_baseline_pending"
      ],
      "future_work_labels": [
        "source_coverage_gap",
        "decomposition_gap",
        "compatibility_evidence_gap"
      ],
      "planner_observed_task_kind": "browse_software",
      "query": "Windows 7 portable apps archive",
      "query_family": "platform_software",
      "query_id": "windows_7_portable_apps_archive",
      "search_mode": "local_index",
      "search_result_count": 11
    },
    {
      "eureka_status": "partial",
      "expected_eureka_current_status": "source_gap",
      "failure_modes": [
        "source_coverage_gap",
        "compatibility_evidence_gap",
        "external_baseline_pending"
      ],
      "future_work_labels": [
        "source_coverage_gap",
        "compatibility_evidence_gap"
      ],
      "planner_observed_task_kind": "identify_software",
      "query": "software to fix broken registry Windows 98",
      "query_family": "platform_software",
      "query_id": "windows_98_registry_repair",
      "search_mode": "local_index",
      "search_result_count": 28
    },
    {
      "eureka_status": "partial",
      "expected_eureka_current_status": "source_gap",
      "failure_modes": [
        "source_coverage_gap",
        "live_source_gap",
        "representation_gap",
        "external_baseline_pending"
      ],
      "future_work_labels": [
        "source_coverage_gap",
        "representation_gap",
        "live_source_gap"
      ],
      "planner_observed_task_kind": "find_documentation",
      "query": "Windows 98 resource kit PDF",
      "query_family": "manual_documentation",
      "query_id": "windows_98_resource_kit_pdf",
      "search_mode": "local_index",
      "search_result_count": 6
    },
    {
      "eureka_status": "partial",
      "expected_eureka_current_status": "source_gap",
      "failure_modes": [
        "source_coverage_gap",
        "compatibility_evidence_gap",
        "ranking_gap",
        "identity_cluster_gap",
        "external_baseline_pending"
      ],
      "future_work_labels": [
        "source_coverage_gap",
        "compatibility_evidence_gap",
        "ranking_gap",
        "identity_cluster_gap"
      ],
      "planner_observed_task_kind": "browse_software",
      "query": "Windows XP FTP clients",
      "query_family": "platform_software",
      "query_id": "windows_xp_ftp_clients",
      "search_mode": "local_index",
      "search_result_count": 31
    },
    {
      "eureka_status": "partial",
      "expected_eureka_current_status": "source_gap",
      "failure_modes": [
        "source_coverage_gap",
        "compatibility_evidence_gap",
        "external_baseline_pending"
      ],
      "future_work_labels": [
        "source_coverage_gap",
        "compatibility_evidence_gap"
      ],
      "planner_observed_task_kind": "browse_software",
      "query": "Windows XP software",
      "query_family": "platform_software",
      "query_id": "windows_xp_software",
      "search_mode": "local_index",
      "search_result_count": 21
    }
  ],
  "total_query_count": 64
}
```

## python scripts/report_external_baseline_status.py --json

status: passed
returncode: 0
```text
reative_ct1740_driver_windows_98",
          "query_text": "Creative CT1740 driver Windows 98",
          "system_id": "internet_archive_full_text_search"
        },
        {
          "batch_id": "batch_0",
          "observation_id": "batch_0::threecom_3c905_windows_95_driver::google_web_search",
          "observation_status": "pending_manual_observation",
          "query_id": "threecom_3c905_windows_95_driver",
          "query_text": "3Com 3C905 Windows 95 driver",
          "system_id": "google_web_search"
        },
        {
          "batch_id": "batch_0",
          "observation_id": "batch_0::threecom_3c905_windows_95_driver::internet_archive_metadata_search",
          "observation_status": "pending_manual_observation",
          "query_id": "threecom_3c905_windows_95_driver",
          "query_text": "3Com 3C905 Windows 95 driver",
          "system_id": "internet_archive_metadata_search"
        },
        {
          "batch_id": "batch_0",
          "observation_id": "batch_0::threecom_3c905_windows_95_driver::internet_archive_full_text_search",
          "observation_status": "pending_manual_observation",
          "query_id": "threecom_3c905_windows_95_driver",
          "query_text": "3Com 3C905 Windows 95 driver",
          "system_id": "internet_archive_full_text_search"
        }
      ],
      "observed_observation_count": 0,
      "observed_query_ids": [],
      "pending_observation_count": 39,
      "selected_query_count": 13,
      "selected_query_ids": [
        "windows_7_apps",
        "windows_7_portable_apps_archive",
        "latest_firefox_before_xp_support_ended",
        "old_blue_ftp_client_xp",
        "windows_98_registry_repair",
        "driver_inf_inside_support_cd",
        "driver_thinkpad_t42_wifi_windows_2000",
        "pc_magazine_july_1994_ray_tracing",
        "mac_os_9_browser",
        "powerpc_osx_104_browser",
        "windows_xp_software",
        "creative_ct1740_driver_windows_98",
        "threecom_3c905_windows_95_driver"
      ],
      "selected_system_count": 3,
      "selected_system_ids": [
        "google_web_search",
        "internet_archive_metadata_search",
        "internet_archive_full_text_search"
      ],
      "status": "pending_manual_observation",
      "status_counts": {
        "pending_manual_observation": 39
      }
    }
  },
  "created_by": "manual_external_baseline_status_report_v0",
  "errors": [],
  "global_slot_counts": {
    "observed": 0,
    "pending_manual_observation": 192
  },
  "limitations": [
    "Pending slots are not observed baselines.",
    "This report performs no external querying or scraping.",
    "Future observed records are manual, time-sensitive, and not global truth."
  ],
  "missing_observation_slots": {
    "google_web_search": 64,
    "internet_archive_full_text_search": 64,
    "internet_archive_metadata_search": 64
  },
  "next_pending_slots": [],
  "observed_query_ids": {
    "google_web_search": 0,
    "internet_archive_full_text_search": 0,
    "internet_archive_metadata_search": 0
  },
  "query_count": 64,
  "query_coverage": {
    "google_web_search": {
      "expected_query_count": 64,
      "observed_query_count": 0,
      "pending_slots": 64
    },
    "internet_archive_full_text_search": {
      "expected_query_count": 64,
      "observed_query_count": 0,
      "pending_slots": 64
    },
    "internet_archive_metadata_search": {
      "expected_query_count": 64,
      "observed_query_count": 0,
      "pending_slots": 64
    }
  },
  "selected_batch": null,
  "status": "ready",
  "status_counts_by_system": {
    "google_web_search": {
      "pending_manual_observation": 64
    },
    "internet_archive_full_text_search": {
      "pending_manual_observation": 64
    },
    "internet_archive_metadata_search": {
      "pending_manual_observation": 64
    }
  },
  "systems": [
    "google_web_search",
    "internet_archive_full_text_search",
    "internet_archive_metadata_search"
  ],
  "validation_status": "valid"
}
```

## python scripts/generate_python_oracle_golden.py --check

status: passed
returncode: 0
```text
Python oracle golden fixture pack
status: passed
fixture_pack_id: python_oracle_golden_v0
fixture_pack_version: 0.1.0
output_root:  <repo> \tests\parity\golden\python_oracle\v0
file_count: 40
```

## python -m unittest discover -s tests/scripts -t .

status: passed
returncode: 0
```text
.........................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 457 tests in 105.502s

OK
```

## python -m unittest discover -s tests/operations -t .

status: passed
returncode: 0
```text
................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 512 tests in 8.724s

OK
```

## python -m unittest discover -s tests/hardening -t .

status: passed
returncode: 0
```text
.....................................................
----------------------------------------------------------------------
Ran 53 tests in 5.499s

OK
```

## python -m unittest discover -s tests/parity -t .

status: passed
returncode: 0
```text
.........................
----------------------------------------------------------------------
Ran 25 tests in 1.394s

OK
```

## python -m unittest discover -s runtime -t .

status: passed
returncode: 0
```text
................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 320 tests in 4.750s

OK
```

## python -m unittest discover -s surfaces -t .

status: passed
returncode: 0
```text
........................................................................................................................................................................
----------------------------------------------------------------------
Ran 168 tests in 31.161s

OK
```

## python -m unittest discover -s tests -t .

status: passed
returncode: 0
```text
..................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 1138 tests in 120.861s

OK
```

## python scripts/check_architecture_boundaries.py

status: passed
returncode: 0
```text
Checked 446 Python files under  <repo> 
No architecture-boundary violations found.
```

## git diff --check

status: passed
returncode: 0
```text
eplaced by CRLF the next time Git touches it
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
warning: in the working copy of 'site/dist/lite/demo-queries.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/lite/evals.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/lite/index.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/lite/limitations.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/lite/search.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/lite/sources.html', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/README.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/demo-queries.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/evals.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/index.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/limitations.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/search.txt', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'site/dist/text/sources.txt', LF will be replaced by CRLF the next time Git touches it
```

## git status --short --branch

status: passed
returncode: 0
```text
## main...origin/main
 M .aide/commands/ci.yaml
 M .aide/commands/dev.yaml
 M .aide/reports/README.md
 M .aide/tasks/audit_backlog.yaml
 M .aide/tasks/queue.yaml
 M contracts/connectors/README.md
 M control/audits/README.md
 M control/inventory/sources/github-releases-recorded-fixtures.source.json
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
 M docs/reference/CANDIDATE_PROMOTION_POLICY.md
 M docs/reference/DEMAND_DASHBOARD_CONTRACT.md
 M docs/reference/EVIDENCE_LEDGER_CONTRACT.md
 M docs/reference/EVIDENCE_PACK_CONTRACT.md
 M docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md
 M docs/reference/PROBE_QUEUE_CONTRACT.md
 M docs/reference/PUBLIC_SEARCH_API_CONTRACT.md
 M docs/reference/PUBLIC_SEARCH_INDEX_FORMAT.md
 M docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md
 M docs/reference/SOURCE_CACHE_CONTRACT.md
 M docs/reference/SOURCE_PACK_CONTRACT.md
 M docs/reference/SOURCE_SYNC_SOURCE_POLICY.md
 M docs/reference/SOURCE_SYNC_WORKER_CONTRACT.md
 M docs/reference/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.md
 M docs/roadmap/BACKEND_ROADMAP.md
 M scripts/README.md
?? contracts/connectors/github_releases_connector_approval.v0.json
?? contracts/connectors/github_releases_connector_manifest.v0.json
?? control/audits/github-releases-connector-approval-v0/
?? control/inventory/connectors/github_releases_connector.json
?? docs/reference/GITHUB_RELEASES_CONNECTOR_APPROVAL.md
?? examples/connectors/github_releases_approval_v0/
?? scripts/dry_run_github_releases_connector_approval.py
?? scripts/validate_github_releases_connector_approval.py
?? scripts/validate_github_releases_connector_contract.py
?? tests/operations/test_github_releases_connector_approval.py
?? tests/scripts/test_dry_run_github_releases_connector_approval.py
?? tests/scripts/test_validate_github_releases_connector_approval.py
?? tests/scripts/test_validate_github_releases_connector_contract.py
```

## cargo --version

status: skipped_unavailable
returncode: None
```text
command target unavailable or optional tool missing
```

## cargo check --workspace --manifest-path crates/Cargo.toml

status: skipped_unavailable
returncode: None
```text
command target unavailable or optional tool missing
```

## cargo test --workspace --manifest-path crates/Cargo.toml

status: skipped_unavailable
returncode: None
```text
command target unavailable or optional tool missing
```
