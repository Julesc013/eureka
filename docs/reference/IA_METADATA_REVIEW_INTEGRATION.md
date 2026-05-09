# IA Metadata Review Integration

IA metadata review integration is the IA-BUNDLE-03 rehearsal of the Track B
local foundry flow. It consumes explicit IA-BUNDLE-02 outputs or committed
fixture-equivalent blocked outputs and creates local review artifacts.

Current behavior:

- Builds IA source-cache review entries.
- Builds IA evidence candidate review entries.
- Builds an IA candidate promotion dry-run.
- Builds an IA pack draft preview.
- Builds a local quality-delta report and connector postmortem.

This is not source acceptance, evidence acceptance, candidate acceptance, pack
acceptance, public truth creation, or public/master index mutation.

For the current bundle, IA-BUNDLE-02 is blocked by policy. IA-BUNDLE-03 uses the
committed blocked generated outputs under
`control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/generated/` and does
not make a new Internet Archive call.

Validation:

```text
python scripts/integrate_ia_metadata_review.py --source-cache-candidate control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/generated/sample_source_cache_candidate_from_live_probe.json --evidence-preview control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/generated/sample_evidence_candidate_preview_from_live_probe.json --check
python scripts/validate_ia_review_integration.py
```
