# PackPage View Model Contract

PackPageView v0 defines the public meaning layer for portable pack summaries.
It is contract and governance work only. It does not implement pack import,
upload, moderation, automatic acceptance, hosted intake, download behavior, or
master-index mutation.

## Purpose

A pack is portable evidence or metadata, not accepted truth. PackPageView makes
pack identity, type, validation posture, contents, provenance, rights/risk/
privacy posture, import status, quarantine status, review status, actions, and
blocked actions visible to every renderer.

Renderers may simplify layout across standard HTML, lite HTML, HTML 3.2-ish,
text, file-tree, API JSON, manifest JSON, future snapshot, future relay,
future terminal, future native-card, and print projections. They must not hide
validation status, lineage, blocked import/upload/acceptance behavior, rights
or risk caveats, limitations, or the fact that pack contents are not public
truth.

## Required Meaning

PackPageView preserves:

- canonical pack identity and route
- pack type and status
- schema, format, checksum, signature, and validation posture
- source, evidence, index, contribution, review, object, source, need, and
  candidate references
- import, staging, quarantine, upload, moderation, automatic-acceptance, public
  search, and master-index impact status
- provenance and lineage
- rights, risk, and privacy posture
- allowed actions and blocked actions
- limitations, warnings, and unresolved gaps

## Current Boundary

Current examples must keep these false or unavailable:

- import runtime, staging runtime, pack import runtime
- hosted upload or submission runtime
- moderation or review runtime
- automatic acceptance
- public search impact
- master-index impact or mutation
- hosted backend, live probes, source sync, downloads, uploads, accounts,
  telemetry, execution, installability, rights clearance, malware safety,
  public acceptance, and production suitability

## Related Contracts

- `contracts/views/pack_page.v0.json`
- `control/inventory/publication/pack_page_view_model_policy.json`
- `contracts/control_schemas/policies/packs/source_pack.v0.json`
- `contracts/control_schemas/policies/packs/evidence_pack.v0.json`
- `contracts/control_schemas/policies/packs/index_pack.v0.json`
- `contracts/control_schemas/policies/packs/contribution_pack.v0.json`
- `docs/reference/SOURCE_PACK_CONTRACT.md`
- `docs/reference/EVIDENCE_PACK_CONTRACT.md`
- `docs/reference/INDEX_PACK_CONTRACT.md`
- `docs/reference/CONTRIBUTION_PACK_CONTRACT.md`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No pack import, upload, moderation, review, or automatic acceptance runtime.
- No hosted backend, source sync, live probes, downloads, uploads, accounts, or
  telemetry.
- No master-index mutation.
- No public truth from pack contents, contribution items, source observations,
  evidence candidates, or AI drafts.
