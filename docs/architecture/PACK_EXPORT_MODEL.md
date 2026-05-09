# Pack Export Model

Pack Export sits after Pack Builder. Pack Builder creates local pack drafts;
Pack Export creates portable local export drafts from those drafts. The export
model deliberately stops before import, submission, upload, publication,
acceptance, public-index mutation, and master-index mutation.

## Request Model

A pack export request records the requested export type, input pack draft ref,
output path, export format, fixity policy, signature policy, review gates,
truth boundary, product boundary, no-goals, and notes.

## Export Record

An export record includes `pack_export_id`, `export_pack_type`,
`export_status`, the summarized input draft, exported pack payload, export
manifest, fixity block, signature placeholder policy, review gates,
limitations, blocked items, validation summary, truth boundary, product
boundary, no-goals, and notes.

## Manifest

The export manifest records the export id, type, format, source draft ref,
fixity, unsigned signature status, review-required marker, and all disabled
downstream authorities. It is not an import manifest and cannot authorize
submission, upload, acceptance, public-index mutation, or master-index mutation.

## Boundaries

Pack Export does not fetch sources, call APIs, call models, perform
observations, write private local state, import packs, submit packs, upload
packs, sign with private keys, accept packs, or mutate public or master indexes.
