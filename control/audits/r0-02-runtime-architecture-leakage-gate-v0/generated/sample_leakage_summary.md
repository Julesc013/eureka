# R0-02 Runtime Architecture Leakage Gate

- status: pass_with_warnings
- production paths scanned: 1654
- known allowlisted violations: 2035
- new violations: 0
- expired allowlist entries: 0
- F0 remains blocked: true
- dev-to-main remains blocked: true

## Top Terms

- truth_boundary: 757
- H2: 675
- product_boundary: 641
- agent: 383
- H1: 195
- BUNDLE: 120
- fixture_only: 107
- review_seed: 86
- MVP: 75
- H3: 68

## New Violations

- none

## Known Temporary Debt

- contracts/ai/ai_provider_manifest.v0.json:156:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:163:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:313:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:321:10 prompt (medium)
- contracts/ai/ai_provider_manifest.v0.json:463:6 prompt (medium)
- contracts/ai/ai_task_request.v0.json:5:123 prompt (medium)
- contracts/ai/README.md:8:10 prompt (medium)
- contracts/archive/schemas/agent.schema.yaml:0:27 agent (medium)
- contracts/archive/schemas/agent.schema.yaml:2:45 agent (medium)
- contracts/archive/schemas/agent.schema.yaml:4:8 agent (medium)
- contracts/archive/schemas/agent.schema.yaml:11:53 agent (medium)
- contracts/archive/schemas/agent.schema.yaml:14:24 agent (medium)
- contracts/archive/schemas/agent.schema.yaml:17:42 agent (medium)
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
