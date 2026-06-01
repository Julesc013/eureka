# LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00

Status: planned

Apply eligible live metadata review previews through the explicit local apply
gate.

Inputs:

- `control/inventory/public_alpha_reassess_02_result.json`
- `control/inventory/live_metadata_review_result.json`
- `examples/review/live_metadata/local_apply_handoff.json`
- `examples/snapshots/refresh/live_metadata_review/reviewed_metadata_preview_section.json`
- `examples/snapshots/refresh/live_metadata_review/reviewed_source_lead_preview_section.json`

Boundary:

- local apply must remain an explicit gate
- no public launch or deployment
- no verified-download, malware-clean, or rights-clearance claims
- no public/master index mutation without governed apply evidence
