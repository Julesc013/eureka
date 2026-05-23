# Source Pack Manifest Contract

A source pack manifest is a portable source-intelligence draft. It can carry
source records, source families, capability names, policy references, connector
family references, coverage records, connector scorecards, limitations, review
posture, and no-live-access posture.

H0-BUNDLE-03 creates pack drafts and export previews only. It does not import,
submit, accept, or publish source packs, and it does not mutate the public or
master index.

Validate with:

```powershell
python scripts/build_source_pack.py --input examples/packs/source/internet_archive_source_pack_manifest_v0.json --check
```
