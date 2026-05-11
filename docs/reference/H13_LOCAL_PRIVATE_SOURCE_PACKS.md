# H13 Local Private Source Packs

H13 defines non-public source boundaries. It is not public source expansion, connector approval, local access approval, or truth acceptance.

Current status: policy-pack-only.

No-goals preserved: no local access, no private access, no user-supplied URL fetch, no authenticated access, no restricted-source access, no filesystem scan, no directory listing, no archive listing, no CAS import, no pack export/import, no source cache or evidence writes, no public/master index mutation, no extraction, no execution, no acquisition, no upload/share/publish behavior, no model/provider calls, and no local/private/restricted/public truth acceptance.

Validation:

- `python scripts/validate_h13_local_private_policy_packs.py`
- `python scripts/summarize_h13_local_private_sources.py --check`
