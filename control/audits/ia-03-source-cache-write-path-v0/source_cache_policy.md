# Source Cache Policy

`control/policies/ia_source_cache_policy.json` enables IA-03 source-cache
writes only for fixture normalized records and IA-02 redacted live-preview
records.

The CLI defaults to dry-run. Apply mode requires an explicit instance path,
`--apply`, and an operator token configured on that instance.

The policy keeps evidence writes, index mutation, downloads, extraction,
model/provider calls, deployment, and public/production readiness claims false.
