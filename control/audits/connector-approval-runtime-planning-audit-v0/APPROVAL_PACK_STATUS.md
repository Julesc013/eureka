# Approval Pack Status

All first-wave approval packs exist and have validators:

- Internet Archive metadata: present, validator present, examples present.
- Wayback/CDX/Memento: present, validator present, examples present.
- GitHub Releases: present, validator present, examples present.
- PyPI metadata: present, validator present, examples present.
- npm metadata: present, validator present, examples present.
- Software Heritage: present, validator present, examples present.

Approval status is `approval_pending` for every connector. The connector
inventories and approval reports record `connector_approved_now: false`.

The approval packs preserve the no-runtime boundary: `live_source_called` and
`external_calls_performed` are false, and no source-cache, evidence-ledger,
candidate, public-index, or master-index mutation is approved by the packs.
