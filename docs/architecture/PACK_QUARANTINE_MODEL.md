# Pack Quarantine Model

The model places quarantine between local pack export and any future import. It preserves review gates and keeps all truth-bearing state unchanged.

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
