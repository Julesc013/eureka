# H13 Restricted Source Manifest Candidate

Restricted source manifest candidates are manifest-only and do not grant direct access.

H13-BUNDLE-02 is fixture-only. It uses committed synthetic fixtures under `examples/connectors/h13_local_private/fixtures/` and does not inspect local disks, folders, archives, media, package caches, NAS shares, object stores, accounts, user URLs, restricted sources, credentials, local files, private URLs, CAS blobs, or packs.

Allowed outputs are normalized boundary records, local source identity candidates, private source boundary candidates, user-supplied URL boundary candidates, authenticated source boundary candidates, restricted source manifest candidates, local CAS import boundary candidates, pack export/import boundary candidates, privacy/redaction candidates, rights/safety candidates, source-cache previews, evidence previews, replay reports, coverage previews, and scorecard previews.

Forbidden outcomes remain blocked: local/private/restricted access, URL fetch, account access, filesystem scan, directory listing, archive listing, file hashing, fingerprinting, malware scanning, CAS import, pack export/import, source-cache writes, evidence writes, review queue writes, public/master index mutation, extraction, execution, acquisition, upload, publication, rights clearance, ownership truth, user authority truth, legal access truth, privacy safety, malware safety, source safety, verified authenticity, production readiness, or public truth.

Validation:

- `python scripts/validate_h13_local_private_fixture_runtime.py`
- `python scripts/replay_h13_local_private_fixtures.py --check`
- `python scripts/summarize_h13_local_private_fixture_outputs.py --input examples/connectors/h13_local_private --check`
