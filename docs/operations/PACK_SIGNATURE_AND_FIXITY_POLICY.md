# Pack Signature And Fixity Policy

SHA-256 is allowed for deterministic local fixity. Private keys, real signing, and real signature verification are deferred unless a future reviewed policy enables them.

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
