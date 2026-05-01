# Human Output Model

Human output prints a compact, operator-readable summary:

- manifest ID and path
- manifest status and staging mode
- validation status
- validate report reference
- staged pack references
- staged entity counts by type and review status
- privacy, rights, and risk posture
- no-mutation summary
- reset/delete/export future operations
- limitations
- next safe action

It explicitly states:

`inspection only; no staging/import/index/search/master-index mutation performed`

This language is required because the inspector success state must not be
confused with staging, import, evidence acceptance, rights clearance, malware
safety, public-search eligibility, or master-index acceptance.
