# Tool Inventory

- generated_by: aide-lite
- source_commit: 6f2698c6e109a3b35d20402bb9871c1e4a674688
- tool_count: 1987
- no_apply: true
- execution_allowed: false
- tool_deletion: false
- tool_rename: false
- tool_migration: false

## Capability Counts

- audit: 464
- build: 107
- context: 569
- docs: 243
- format: 14
- generate: 129
- install: 87
- package: 422
- release: 255
- repo_policy: 385
- security: 2
- test: 72
- unknown: 277
- validate: 549

## Tools

- `.aide/adapters/templates/continue-checks.template.md`: capabilities=validate risk=medium fate=wrap
- `.aide/cache/latest-cache-keys.json`: capabilities=test risk=medium fate=wrap
- `.aide/cache/latest-cache-keys.md`: capabilities=test risk=medium fate=wrap
- `.aide/changelog/RELEASE_NOTES.preview.md`: capabilities=release risk=release fate=wrap
- `.aide/context/latest-context-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/latest-review-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/latest-task-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/test-map.json`: capabilities=context,test risk=medium fate=wrap
- `.aide/controller/latest-outcome-report.md`: capabilities=audit,repo_policy,test risk=medium fate=wrap
- `.aide/controller/latest-recommendations.md`: capabilities=test risk=medium fate=wrap
- `.aide/evals/runs/latest-golden-tasks.json`: capabilities=test risk=medium fate=wrap
- `.aide/evals/runs/latest-golden-tasks.md`: capabilities=test risk=medium fate=wrap
- `.aide/gateway/latest-gateway-status.json`: capabilities=test risk=medium fate=wrap
- `.aide/gateway/latest-gateway-status.md`: capabilities=test risk=medium fate=wrap
- `.aide/git/latest-helper-plan.json`: capabilities=test risk=medium fate=wrap
- `.aide/git/latest-helper-plan.md`: capabilities=test risk=medium fate=wrap
- `.aide/git/sync-policy.md`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/hooks/commit-msg`: capabilities=unknown risk=unknown fate=unknown
- `.aide/import-policy.template.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/import-policy.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/import-report.template.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/policies/export-import.yaml`: capabilities=unknown risk=unknown fate=unknown
- `.aide/policies/sync-policy.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/prompts/AIDE-SYNC-01.md`: capabilities=unknown risk=unknown fate=unknown
- `.aide/providers/latest-provider-status.json`: capabilities=test risk=medium fate=wrap
- `.aide/providers/latest-provider-status.md`: capabilities=test risk=medium fate=wrap
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/import-review.md`: capabilities=unknown risk=unknown fate=unknown
- `.aide/queue/EUREKA-AIDE-PILOT-01/import-report.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/queue/EUREKA-AIDE-SYNC-01/evidence/sync-report.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01/evidence/install-upgrade-risk-report.md`: capabilities=audit,install,repo_policy risk=medium fate=wrap
- `.aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01/evidence/release-bundle-readiness.md`: capabilities=install,package,release risk=release fate=wrap
- `.aide/queue/TRACK-A-11/evidence/track-a-audit-result.md`: capabilities=audit risk=medium fate=wrap
- `.aide/repo/generated-map.json`: capabilities=generate,repo_policy risk=medium fate=wrap
- `.aide/repo/latest-repo-intelligence.md`: capabilities=repo_policy,test risk=medium fate=wrap
- `.aide/repo/test-map.json`: capabilities=repo_policy,test risk=medium fate=wrap
- `.aide/reports/eureka-fresh-upgrade-preflight.md`: capabilities=audit,install,repo_policy risk=medium fate=wrap
- `.aide/reports/eureka-release-bundle-readiness.md`: capabilities=audit,package,release,repo_policy risk=release fate=wrap
- `.aide/routing/latest-route-decision.json`: capabilities=test risk=medium fate=wrap
- `.aide/routing/latest-route-decision.md`: capabilities=test risk=medium fate=wrap
- `.aide/scripts/aide_lite.py`: capabilities=context,repo_policy,test,validate risk=medium fate=keep
- `.aide/tasks/audit_backlog.yaml`: capabilities=audit risk=medium fate=wrap
- `.aide/verification/latest-verification-report.md`: capabilities=audit,repo_policy,test risk=medium fate=wrap
- `.github/workflows/pages.yml`: capabilities=unknown risk=unknown fate=unknown
- `contracts/actions/export_manifest.v0.json`: capabilities=unknown risk=unknown fate=unknown
- `contracts/connectors/github_releases_connector_approval.v0.json`: capabilities=release risk=release fate=wrap
- `contracts/connectors/github_releases_connector_manifest.v0.json`: capabilities=release risk=release fate=wrap
- `contracts/master_index/reviewed_public_index_rebuild.v0.json`: capabilities=build risk=medium fate=wrap
- `contracts/native/native_build_evidence.v0.json`: capabilities=build risk=medium fate=wrap
- `contracts/native/native_build_log_record.v0.json`: capabilities=build risk=medium fate=wrap
- `contracts/native/native_manual_build_packet.v0.json`: capabilities=build,context risk=medium fate=wrap
- `contracts/native/native_manual_smoke_checklist.v0.json`: capabilities=validate risk=low fate=wrap
- `contracts/runtime/live_metadata_test_request.v0.json`: capabilities=test risk=release fate=wrap
- `contracts/runtime/live_metadata_test_result.v0.json`: capabilities=test risk=release fate=wrap
- `contracts/source_sync/source_sync_job_kind.v0.json`: capabilities=unknown risk=unknown fate=unknown
- `contracts/source_sync/source_sync_worker_job.v0.json`: capabilities=unknown risk=unknown fate=unknown
- `contracts/source_sync/source_sync_worker_manifest.v0.json`: capabilities=unknown risk=unknown fate=unknown
- `contracts/stores/public_index_rebuild.v0.json`: capabilities=build risk=medium fate=wrap
- `contracts/ui/ui_contracts/stored_exports.ui_contract.yaml`: capabilities=unknown risk=unknown fate=unknown
- `contracts/ui/view_models/stored_exports.view_model.yaml`: capabilities=unknown risk=unknown fate=unknown
- `control/audits/2026-04-25-comprehensive-test-eval-audit/AUDIT_SUMMARY.md`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/2026-04-25-comprehensive-test-eval-audit/BEHAVIOR_AUDIT.md`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/2026-04-25-comprehensive-test-eval-audit/CONTENT_COVERAGE_AUDIT.md`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/2026-04-25-comprehensive-test-eval-audit/HARD_TEST_PROPOSALS.md`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/2026-04-25-comprehensive-test-eval-audit/STRUCTURE_AUDIT.md`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/2026-04-25-comprehensive-test-eval-audit/TEST_BACKLOG.json`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/2026-04-25-comprehensive-test-eval-audit/TEST_GAP_AUDIT.md`: capabilities=audit,test risk=medium fate=wrap
- `control/audits/c-bundle-01-native-skeleton-matrix-winforms-v0/native_build_evidence_report.md`: capabilities=audit,build,package,repo_policy risk=medium fate=wrap
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/generated/sample_native_build_evidence_plan.json`: capabilities=audit,build,generate,package risk=medium fate=wrap
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/generated/sample_native_smoke_checklist.json`: capabilities=audit,generate,package,validate risk=medium fate=wrap
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/native_manual_build_evidence_plan.md`: capabilities=audit,build,package risk=medium fate=wrap
- `control/audits/c-bundle-02-native-first-wave-skeletons-v0/native_smoke_checklist_summary.md`: capabilities=audit,package,validate risk=low fate=wrap
- `control/audits/c-bundle-03-native-smoke-packaging-v0/generated/sample_native_release_candidate_preview.json`: capabilities=audit,context,generate,package,release risk=release fate=wrap
- `control/audits/c-bundle-03-native-smoke-packaging-v0/generated/sample_track_c_integration_audit.json`: capabilities=audit,context,generate,package risk=medium fate=wrap
- `control/audits/c-bundle-03-native-smoke-packaging-v0/native_build_log_summary.md`: capabilities=audit,build,context,package risk=medium fate=wrap
- `control/audits/c-bundle-03-native-smoke-packaging-v0/native_first_wave_integration_audit.md`: capabilities=audit,context,package risk=medium fate=wrap
- `control/audits/c-bundle-03-native-smoke-packaging-v0/native_no_release_binary_report.md`: capabilities=audit,context,package,release,repo_policy risk=release fate=wrap
- `control/audits/c-bundle-03-native-smoke-packaging-v0/native_release_candidate_preview_summary.md`: capabilities=audit,context,package,release risk=release fate=wrap
- `control/audits/comparison-page-contract-v0/NO_DOWNLOAD_INSTALL_EXECUTION_POLICY.md`: capabilities=audit,install,repo_policy risk=medium fate=wrap
- `control/audits/comparison-page-contract-v0/VERSION_STATE_RELEASE_COMPARISON_MODEL.md`: capabilities=audit,release risk=release fate=wrap
- `control/audits/compatibility-aware-ranking-contract-v0/ACTION_SAFETY_AND_INSTALLABILITY_CAUTION_MODEL.md`: capabilities=audit,install risk=medium fate=wrap

## Warnings

- unknown_tool_candidates: .aide/hooks/commit-msg, .aide/policies/export-import.yaml, .aide/prompts/AIDE-SYNC-01.md, .aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/import-review.md, .github/workflows/pages.yml, contracts/actions/export_manifest.v0.json, contracts/source_sync/source_sync_job_kind.v0.json, contracts/source_sync/source_sync_worker_job.v0.json, contracts/source_sync/source_sync_worker_manifest.v0.json, contracts/ui/ui_contracts/stored_exports.ui_contract.yaml, contracts/ui/view_models/stored_exports.view_model.yaml, control/inventory/git/sync_workflow_commands.json
- high_risk_tool_candidates: .aide/changelog/RELEASE_NOTES.preview.md, .aide/queue/EUREKA-AIDE-UPGRADE-PREFLIGHT-01/evidence/release-bundle-readiness.md, .aide/reports/eureka-release-bundle-readiness.md, contracts/connectors/github_releases_connector_approval.v0.json, contracts/connectors/github_releases_connector_manifest.v0.json, contracts/runtime/live_metadata_test_request.v0.json, contracts/runtime/live_metadata_test_result.v0.json, control/audits/c-bundle-03-native-smoke-packaging-v0/generated/sample_native_release_candidate_preview.json, control/audits/c-bundle-03-native-smoke-packaging-v0/native_no_release_binary_report.md, control/audits/c-bundle-03-native-smoke-packaging-v0/native_release_candidate_preview_summary.md, control/audits/comparison-page-contract-v0/VERSION_STATE_RELEASE_COMPARISON_MODEL.md, control/audits/connector-approval-runtime-planning-audit-v0/GITHUB_RELEASES_REVIEW.md

## Next

- Q42 Move Map / Salvage Map / Path Alias v0.
