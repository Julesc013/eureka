# H13 Privacy Redaction Policy

Private paths, account identifiers, user identifiers, credentials, tokens, private URLs, and sensitive filenames must be redacted or hashed in public-safe outputs. Redaction does not prove public safety.

Current status: policy-pack-only.

No-goals preserved: no local access, no private access, no user-supplied URL fetch, no authenticated access, no restricted-source access, no filesystem scan, no directory listing, no archive listing, no CAS import, no pack export/import, no source cache or evidence writes, no public/master index mutation, no extraction, no execution, no acquisition, no upload/share/publish behavior, no model/provider calls, and no local/private/restricted/public truth acceptance.

Validation:

- `python scripts/validate_h13_local_private_policy_packs.py`
- `python scripts/summarize_h13_local_private_sources.py --check`
