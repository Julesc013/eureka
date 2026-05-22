# R0 Legacy Runtime Leakage Remediation

R0-REMEDIATION-LEGACY-LEAKAGE-01 retired the largest known source of runtime architecture leakage by quarantining H-series connector prototype packages out of production runtime scope.

Before remediation, the fresh runtime architecture leakage audit reported 22,727 known allowlisted findings. Of those, 19,248 findings came from task-shaped connector packages under `runtime/connectors/h*`.

## What Moved

The following legacy connector prototype packages moved from `runtime/connectors/` to `archive/prototypes/legacy_runtime/connectors/`:

- `h1_metadata_wave`
- `h2_package_registries`
- `h3_os_package_archives`
- `h4_code_source_release`
- `h5_vendor_update_driver`
- `h6_web_archive_news_event`
- `h7_library_research`
- `h8_manuals_docs_standards`
- `h9_media_metadata`
- `h10_games_emulation`
- `h11_storefront`
- `h12_retro_community`
- `h13_local_private`
- `h14_source_discovery`

Active script and test references were updated to import from the quarantine namespace. Historical audit evidence was left historical.

## What Was Retired

The remediation retired 1,866 exact allowlist entries that pointed at the moved `runtime/connectors/h*` paths.

After remediation:

- known allowlisted findings: 3,507
- remaining allowlist entries: 2,267
- new unallowlisted production leaks: 0
- clean R0 runtime seams remained clean

## What Remains

Remaining allowlist debt is outside the recovered R0 product seams. It includes older non-H-series runtime, surface, contract, and local-foundry terminology that still needs explicit future review before main promotion.

The remaining allowlist is warning-level debt, not production readiness evidence. Entries retain explicit reasons, owners, replacements, expiration tasks, and severity after expiry.

## F0 And Promotion Decision

F0 may resume in principle because the recovered R0 seams remain clean and no new unallowlisted production leaks were introduced.

Dev-to-main remains `promotion_plan_only`; this task did not merge branches, deploy, regenerate site output, mutate a master index, or claim production/public launch readiness.
