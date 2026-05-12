# R0-02 Runtime Architecture Leakage Gate

- status: pass_with_warnings
- production paths scanned: 2004
- known allowlisted violations: 29015
- new violations: 0
- expired allowlist entries: 0
- F0 remains blocked: true
- dev-to-main remains blocked: true

## Top Terms

- phase_named_runtime_symbol: 6693
- BUNDLE: 4469
- truth_boundary: 2352
- product_boundary: 2303
- review_seed: 1185
- H9: 985
- H2: 951
- H10: 807
- H8: 782
- H7: 742

## New Violations

- none

## Known Temporary Debt

- contracts/actions/acquisition_manifest.v0.json:23:6 truth_boundary (medium)
- contracts/actions/acquisition_manifest.v0.json:24:6 product_boundary (medium)
- contracts/actions/acquisition_manifest.v0.json:30:6 truth_boundary (medium)
- contracts/actions/action_manifest.v0.json:21:6 truth_boundary (medium)
- contracts/actions/action_manifest.v0.json:22:6 product_boundary (medium)
- contracts/actions/action_manifest.v0.json:57:6 truth_boundary (medium)
- contracts/actions/action_manifest.v0.json:68:6 product_boundary (medium)
- contracts/actions/action_policy.v0.json:19:6 truth_boundary (medium)
- contracts/actions/action_policy.v0.json:20:6 product_boundary (medium)
- contracts/actions/action_policy.v0.json:37:6 truth_boundary (medium)
- contracts/actions/action_policy.v0.json:38:6 product_boundary (medium)
- contracts/actions/action_result_preview.v0.json:15:6 truth_boundary (medium)
- contracts/actions/action_result_preview.v0.json:16:6 product_boundary (medium)
- contracts/actions/action_result_preview.v0.json:21:35 preview_only (medium)
- contracts/actions/action_taxonomy.v0.json:12:6 truth_boundary (medium)
- contracts/actions/action_taxonomy.v0.json:13:6 product_boundary (medium)
- contracts/actions/action_taxonomy.v0.json:70:6 truth_boundary (medium)
- contracts/actions/action_taxonomy.v0.json:71:6 product_boundary (medium)
- contracts/actions/blocked_action_report.v0.json:17:6 truth_boundary (medium)
- contracts/actions/blocked_action_report.v0.json:18:6 product_boundary (medium)
- contracts/actions/citation_bundle.v0.json:0:28 BUNDLE (medium)
- contracts/actions/citation_bundle.v0.json:3:59 BUNDLE (medium)
- contracts/actions/citation_bundle.v0.json:4:29 BUNDLE (medium)
- contracts/actions/citation_bundle.v0.json:8:15 BUNDLE (medium)
- contracts/actions/citation_bundle.v0.json:19:6 truth_boundary (medium)
