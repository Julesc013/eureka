# Pack Quarantine Runtime

Pack quarantine reads explicit local pack exports and produces review-gated quarantine results, fixity reports, signature-envelope validation reports, import previews, and review seeds. It is not import, submission, publication, upload, acceptance, or trust creation.

## Boundaries

- Pack import: false
- Pack submission: false
- Hosted upload: false
- Pack acceptance: false
- Evidence acceptance: false
- Candidate acceptance: false
- Public index mutation: false
- Master index mutation: false
- Rights clearance claims: false
- Malware safety claims: false
- Verified installability claims: false

## Validation

Run `python scripts/validate_pack_quarantine_runtime.py` plus the focused quarantine, fixity, import-preview, summary, and unittest commands from I-BUNDLE-01.
