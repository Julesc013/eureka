# R0-02 Runtime Architecture Leakage Gate

- status: pass_with_warnings
- production paths scanned: 1033
- known allowlisted violations: 1954
- new violations: 0
- expired allowlist entries: 0
- F0 remains blocked: true
- dev-to-main remains blocked: true

## Top Terms

- truth_boundary: 757
- product_boundary: 641
- H2: 550
- H1: 134
- BUNDLE: 132
- review_seed: 81
- fixture_only: 77
- agent: 50
- review_seed_identifier: 49
- quality_delta: 36

## New Violations

- none

## Known Temporary Debt

- contracts/command/actions/acquisition_manifest.v0.json:23:6 truth_boundary (medium)
- contracts/command/actions/acquisition_manifest.v0.json:24:6 product_boundary (medium)
- contracts/command/actions/acquisition_manifest.v0.json:30:6 truth_boundary (medium)
- contracts/command/actions/action_manifest.v0.json:21:6 truth_boundary (medium)
- contracts/command/actions/action_manifest.v0.json:22:6 product_boundary (medium)
- contracts/command/actions/action_manifest.v0.json:57:6 truth_boundary (medium)
- contracts/command/actions/action_manifest.v0.json:68:6 product_boundary (medium)
- contracts/command/actions/action_policy.v0.json:19:6 truth_boundary (medium)
- contracts/command/actions/action_policy.v0.json:20:6 product_boundary (medium)
- contracts/command/actions/action_policy.v0.json:37:6 truth_boundary (medium)
- contracts/command/actions/action_policy.v0.json:38:6 product_boundary (medium)
- contracts/command/actions/compare_action_manifest.v0.json:15:6 truth_boundary (medium)
- contracts/command/actions/compare_action_manifest.v0.json:16:6 product_boundary (medium)
- contracts/command/actions/export_manifest.v0.json:19:6 truth_boundary (medium)
- contracts/command/actions/export_manifest.v0.json:20:6 product_boundary (medium)
- contracts/command/actions/export_manifest.v0.json:26:6 truth_boundary (medium)
- contracts/command/actions/preservation_manifest.v0.json:19:6 truth_boundary (medium)
- contracts/command/actions/preservation_manifest.v0.json:20:6 product_boundary (medium)
- contracts/command/actions/preservation_manifest.v0.json:25:6 truth_boundary (medium)
- contracts/ai/ai_provider_manifest.v0.json:156:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:163:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:313:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:321:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:463:6 prompt (medium)
- contracts/ai/ai_task_request.v0.json:5:123 prompt (medium)
