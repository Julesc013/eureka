# H3 OS Package Identity Policy

Defines OS package identity candidates across package names, source packages, distributions, releases, architectures, versions, revisions, hashes, and PURL-style mapping. Identity candidates remain candidates and are not accepted truth.

## Scope

- wave_id: `H3`
- source_family: `os_package_archive`
- current_status: `policy_pack_only`
- source_count: `13`

## Boundaries

- live_access_enabled: `false`
- source_sync_enabled: `false`
- repository_index_fetch_enabled: `false`
- package_download_enabled: `false`
- package_manager_invocation_enabled: `false`
- install_execute_enabled: `false`
- public_index_mutated: `false`
- master_index_mutated: `false`

## Next

H3-BUNDLE-02 may add committed-fixture-only runtimes and normalizers. H3-BUNDLE-03 may later define approval-gated metadata-only live probes. Neither future task may infer live approval, download permission, installability, rights clearance, malware safety, dependency correctness, compatibility correctness, or production readiness from this policy pack.
