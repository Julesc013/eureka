# Field Stability Matrix

Field paths use dotted JSON notation. `[]` means each item in an array.

## `site_manifest.json`

| Field path | Current presence | Stability | Consumer guidance | Notes |
| --- | --- | --- | --- | --- |
| `schema_version` | present | `stable_draft` | Check before interpreting the file. | Version is `0.1.0`. |
| `generated_by` | present | `stable_draft` | Display or validate generator provenance. | Static generator only. |
| `artifact` | present | `stable_draft` | Use as high-level public data artifact label. | Currently `public_site/data`. |
| `current_static_artifact` | present | `stable_draft` | Display current static artifact root. | Currently `public_site`. |
| `public_data_files[]` | present | `stable_draft` | Discover generated public data files. | Does not imply live API routes. |
| `contains_live_backend` | present | `stable_draft` | Must remain false until a later contract changes it. | Safety flag. |
| `contains_live_probes` | present | `stable_draft` | Must remain false until a later contract changes it. | Safety flag. |
| `contains_external_observations` | present | `stable_draft` | Must remain false until human observations exist. | Safety flag. |
| `no_deployment_claim` | present | `stable_draft` | Use to avoid deployment overclaims. | Safety flag. |
| `base_path_targets[]` | present | `stable_draft` | Display supported static base path targets. | Not a deployment proof. |
| `pages[]` | present | `experimental` | Prefer `page_registry.json` for route details. | Copy of page summary. |
| `deployment_targets[]` | present | `experimental` | Display only. | Deployment success remains unverified. |
| `static_hosting_targets[]` | present | `experimental` | Display only. | Future host portability. |
| `live_backend_handoff` | present | `experimental` | Display disabled/future contract posture. | Not a live API. |
| `live_probe_gateway` | present | `experimental` | Display disabled/future probe posture. | No network calls. |
| `action_policy` | present | `experimental` | Display disabled risky-action posture. | Not action implementation. |
| `local_cache_privacy_policy` | present | `experimental` | Display privacy defaults. | Not cache implementation. |
| `relay_surface` | present | `experimental` | Display relay future/deferred posture. | No relay exists. |
| `snapshot_format` | present | `experimental` | Display seed snapshot contract posture. | Not production signing. |
| `surface_capabilities[]` | present | `experimental` | Display surface status only. | Do not branch as stable API. |
| `limitations[]` | present | `experimental` | Show limitations to users. | Text may change. |
| `source_inputs[]` | present | `internal` | Diagnostic only. | Repo path list. |

## `page_registry.json`

| Field path | Current presence | Stability | Consumer guidance | Notes |
| --- | --- | --- | --- | --- |
| `schema_version` | present | `stable_draft` | Check before interpreting the file. | Version is `0.1.0`. |
| `generated_by` | present | `stable_draft` | Display generator provenance. | Static generator only. |
| `registry_id` | present | `stable_draft` | Identify registry kind. | Public page registry. |
| `artifact_root` | present | `stable_draft` | Display artifact root. | Currently `public_site`. |
| `pages[].path` | present | `stable_draft` | Safe for static clients to list/link. | Reserved paths may be unimplemented. |
| `pages[].title` | present | `stable_draft` | Safe display label. | Text can be corrected without semantic break. |
| `pages[].status` | present | `stable_draft` | Safe to distinguish implemented/static_demo/planned/deferred. | Status vocabulary remains governed. |
| `pages[].stability` | present | `stable_draft` | Safe to show route stability. | Route stability, not field stability. |
| `pages[].client_profiles[]` | present | `stable_draft` | Safe to show intended profiles. | Profiles may grow. |
| `pages[].requires_javascript` | present | `stable_draft` | Safe compatibility signal. | Boolean. |
| `pages[].works_under_project_base_path` | present | `stable_draft` | Safe portability signal. | Boolean. |
| `pages[].safe_for_static_hosting` | present | `stable_draft` | Safe static-host signal. | Boolean. |
| `route_count` | present | `stable_draft` | Display current count. | Value may change without breaking. |
| `implemented_route_count` | present | `stable_draft` | Display current count. | Value may change without breaking. |
| `reserved_route_count` | present | `stable_draft` | Display current count. | Value may change without breaking. |
| `pages[].source_file` | present | `internal` | Do not consume as public API. | Repo path diagnostic. |
| `source_inputs[]` | present | `internal` | Diagnostic only. | Repo path list. |
| `limitations[]` | present | `experimental` | Display only. | Text may change. |

## `source_summary.json`

| Field path | Current presence | Stability | Consumer guidance | Notes |
| --- | --- | --- | --- | --- |
| `schema_version` | present | `stable_draft` | Check before interpreting the file. | Version is `0.1.0`. |
| `generated_by` | present | `stable_draft` | Display generator provenance. | Static generator only. |
| `source_count` | present | `stable_draft` | Display current count. | Value may change as sources are added. |
| `sources[].source_id` | present | `stable_draft` | Safe for static clients to display/link and for snapshots to reference. | Do not infer live access. |
| `sources[].label` | present | `stable_draft` | Safe display label. | Text can be corrected. |
| `sources[].family` | present | `stable_draft` | Safe display grouping. | Family vocabulary may grow. |
| `sources[].status` | present | `stable_draft` | Safe to distinguish active fixture, placeholder, and local-private future. | Status vocabulary remains governed. |
| `sources[].posture` | present | `stable_draft` | Safe to display summary posture. | Not a connector contract. |
| `sources[].coverage_depth` | present | `stable_draft` | Safe to display current coverage depth. | Vocabulary may grow by version. |
| `sources[].fixture_backed` | present | `stable_draft` | Safe boolean display. | Does not imply real-world coverage. |
| `sources[].recorded_fixture_backed` | present | `stable_draft` | Safe boolean display. | Does not imply live API support. |
| `sources[].placeholder` | present | `stable_draft` | Safe placeholder warning. | Must remain honest. |
| `sources[].future_marker` | present | `stable_draft` | Safe future/deferred warning. | Must remain honest. |
| `sources[].live_supported` | present | `stable_draft` | Safe no-live signal. | False today. |
| `sources[].live_deferred` | present | `stable_draft` | Safe future-live signal. | Does not approve probes. |
| `contains_live_data` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_live_probes` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_external_observations` | present | `stable_draft` | Must remain false. | Safety flag. |
| `sources[].capabilities` | present | `experimental` | Display only; avoid branching on individual booleans unless version-pinned. | Capability shape may evolve. |
| `sources[].capabilities.supported[]` | present | `experimental` | Display only. | Derived list. |
| `sources[].limitations[]` | present | `volatile` | Display text only. | Wording may change. |
| `sources[].next_step` | present | `volatile` | Display text only. | Planning note. |
| `status_counts` | present | `experimental` | Display current aggregate only. | Keys may grow. |
| `source_inputs[]` | present | `internal` | Diagnostic only. | Repo glob. |

## `eval_summary.json`

| Field path | Current presence | Stability | Consumer guidance | Notes |
| --- | --- | --- | --- | --- |
| `schema_version` | present | `stable_draft` | Check before interpreting the file. | Version is `0.1.0`. |
| `generated_by` | present | `stable_draft` | Display generator provenance. | Static generator only. |
| `contains_live_data` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_live_probes` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_external_observations` | present | `stable_draft` | Must remain false unless human observations exist. | Safety flag. |
| `archive_resolution.task_count` | present | `experimental` | Display current local eval count. | Not production relevance. |
| `archive_resolution.status_counts` | present | `experimental` | Display current local status summary. | Taxonomy may evolve. |
| `search_usefulness.query_count` | present | `experimental` | Display current local audit count. | Not production benchmark. |
| `search_usefulness.status_counts` | present | `experimental` | Display current local status summary. | Taxonomy may evolve. |
| `search_usefulness.failure_mode_counts` | present | `volatile` | Display as current audit detail only. | Failure taxonomy changes. |
| `manual_external_baselines.global_pending_count` | present | `experimental` | Display pending manual slots. | Value may change. |
| `manual_external_baselines.global_observed_count` | present | `experimental` | Display observed count only if records exist. | Currently zero. |
| `manual_external_baselines.batch_0_pending_count` | present | `experimental` | Display pending Batch 0 slots. | Value may change. |
| `manual_external_baselines.batch_0_observed_count` | present | `experimental` | Display observed Batch 0 count. | Currently zero. |
| `source_inputs[]` | present | `internal` | Diagnostic only. | Command list. |
| `archive_resolution.source_command` | present | `internal` | Diagnostic only. | Command string. |
| `search_usefulness.source_command` | present | `internal` | Diagnostic only. | Command string. |
| `manual_external_baselines.source_command` | present | `internal` | Diagnostic only. | Command string. |
| `limitations[]` | present | `experimental` | Display limitations. | Text may change. |

## `route_summary.json`

| Field path | Current presence | Stability | Consumer guidance | Notes |
| --- | --- | --- | --- | --- |
| `schema_version` | present | `stable_draft` | Check before interpreting the file. | Version is `0.1.0`. |
| `generated_by` | present | `stable_draft` | Display generator provenance. | Static generator only. |
| `public_alpha_not_production` | present | `stable_draft` | Must stay true for this summary. | Safety flag. |
| `contains_live_backend` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_live_probes` | present | `stable_draft` | Must remain false. | Safety flag. |
| `route_counts.total` | present | `stable_draft` | Display current route inventory count. | Value may change. |
| `route_counts.safe_public_alpha` | present | `stable_draft` | Display current route posture count. | Value may change. |
| `route_counts.blocked_public_alpha` | present | `stable_draft` | Display current route posture count. | Value may change. |
| `route_counts.local_dev_only` | present | `stable_draft` | Display current route posture count. | Value may change. |
| `route_counts.review_required` | present | `stable_draft` | Display current route posture count. | Value may change. |
| `classification_counts` | present | `experimental` | Display aggregate only. | Keys may grow. |
| `review_required_routes[]` | present | `experimental` | Display current review-required examples only. | Route details may change. |
| `blocked_routes[]` | present | `experimental` | Display current blocked examples only. | Route details may change. |
| `source_inputs[]` | present | `internal` | Diagnostic only. | Repo path list. |
| `limitations[]` | present | `experimental` | Display limitations. | Text may change. |

## `build_manifest.json`

| Field path | Current presence | Stability | Consumer guidance | Notes |
| --- | --- | --- | --- | --- |
| `schema_version` | present | `stable_draft` | Check before interpreting the file. | Version is `0.1.0`. |
| `generated_by` | present | `stable_draft` | Display generator provenance. | Static generator only. |
| `repo` | present | `stable_draft` | Display repo identity. | Not deployment proof. |
| `branch` | present | `stable_draft` | Display branch label. | Current static artifact branch. |
| `artifact_root` | present | `stable_draft` | Display static artifact root. | Currently `public_site`. |
| `data_files[]` | present | `stable_draft` | Discover generated public data files. | Not live API discovery. |
| `contains_live_backend` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_live_probes` | present | `stable_draft` | Must remain false. | Safety flag. |
| `contains_external_observations` | present | `stable_draft` | Must remain false unless human evidence exists. | Safety flag. |
| `deployment_performed` | present | `stable_draft` | Must remain false for committed static artifact. | Safety flag. |
| `downloads_enabled` | present | `stable_draft` | Must remain false. | Safety flag. |
| `install_automation_enabled` | present | `stable_draft` | Must remain false. | Safety flag. |
| `malware_scanning_claimed` | present | `stable_draft` | Must remain false. | Safety flag. |
| `rights_clearance_claimed` | present | `stable_draft` | Must remain false. | Safety flag. |
| `local_cache_runtime_implemented` | present | `stable_draft` | Must remain false. | Safety flag. |
| `private_ingestion_implemented` | present | `stable_draft` | Must remain false. | Safety flag. |
| `telemetry_implemented` | present | `stable_draft` | Must remain false. | Safety flag. |
| `accounts_implemented` | present | `stable_draft` | Must remain false. | Safety flag. |
| `cloud_sync_implemented` | present | `stable_draft` | Must remain false. | Safety flag. |
| `commit` | present | `volatile` | Diagnostic only. | `UNKNOWN_UNTIL_CI` in committed artifact. |
| `built_at` | present | `volatile` | Diagnostic only. | `UNKNOWN_UNTIL_CI` in committed artifact. |
| `source` | present | `internal` | Diagnostic only. | Generator slice id. |
| `source_inputs[]` | present | `internal` | Diagnostic only. | Repo path and command list. |
| `validations_expected[]` | present | `internal` | Diagnostic only. | Command list may change. |
| `action_policy` | present | `experimental` | Display disabled risky-action posture. | Not action implementation. |
| `local_cache_privacy_policy` | present | `experimental` | Display privacy defaults. | Not cache implementation. |
