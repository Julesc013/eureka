# H13 Local Private Fixture Plan

H13-BUNDLE-02 should add fixture-only boundary records: minimal policy record, redacted local source identity metadata, private source boundary, user-supplied URL boundary with no fetch, authenticated source boundary with no credentials, restricted manifest-only record, local CAS import boundary with no files, pack export/import boundary with no packs, privacy/redaction fixture, rights/safety fixture, policy-blocked record, malformed/partial record, and explicit no-access evidence.

Current status: policy-pack-only.

No-goals preserved: no local access, no private access, no user-supplied URL fetch, no authenticated access, no restricted-source access, no filesystem scan, no directory listing, no archive listing, no CAS import, no pack export/import, no source cache or evidence writes, no public/master index mutation, no extraction, no execution, no acquisition, no upload/share/publish behavior, no model/provider calls, and no local/private/restricted/public truth acceptance.

Validation:

- `python scripts/validate_h13_local_private_policy_packs.py`
- `python scripts/summarize_h13_local_private_sources.py --check`
