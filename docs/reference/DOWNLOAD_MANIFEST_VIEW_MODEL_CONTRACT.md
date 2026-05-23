# DownloadManifest View Model Contract

DownloadManifestView v0 defines the public meaning layer for acquisition,
export, citation, snapshot, relay, and native-handoff manifest pages. It is
contract and governance work only. It does not enable downloads, installers,
execution, package-manager handoff, native handoff, relay runtime, or hosted
file service behavior.

## Purpose

A download manifest is not a downloader. DownloadManifestView makes manifest
identity, target object and representation refs, source refs, access posture,
file metadata, checksums, signatures, rights/risk/privacy/safety posture,
allowed actions, blocked actions, limitations, and future handoff status visible
to every renderer.

## Required Meaning

DownloadManifestView preserves:

- canonical manifest identity and route
- target object, representation, source, and pack refs
- access path status and unavailable download/install/execution posture
- checksum and signature posture without authenticity overclaiming
- rights, risk, privacy, and safety posture
- native, relay, and snapshot handoff status as future/deferred only
- allowed actions and blocked actions
- limitations, warnings, and unresolved gaps

## Current Boundary

Current examples must keep these unavailable or false:

- direct downloads, installers, execution, package-manager handoff, native
  handoff, relay handoff, hosted file service, uploads, accounts, and telemetry
- hosted backend, live probes, source sync, source connectors, and product
  runtime changes
- rights clearance, malware safety, verified installability, safe execution,
  authorized downloads, or production suitability

## Related Contracts

- `contracts/view/pages/download_manifest_page.v0.json`
- `control/inventory/publication/download_manifest_view_model_policy.json`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`
- `docs/reference/EVIDENCE_PACK_CONTRACT.md`
- `docs/reference/SOURCE_PACK_CONTRACT.md`
- `docs/reference/INDEX_PACK_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No downloads, installers, execution, package-manager handoff, relay runtime,
  native handoff runtime, uploads, accounts, telemetry, or hosted backend claim.
- No rights clearance, malware safety, verified installability, or safe
  execution claims.
