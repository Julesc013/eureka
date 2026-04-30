# Public-Alpha Review

Public-alpha remains a constrained local/prototype posture. The route inventory
classifies the public search routes as `safe_public_alpha` only because they are
read-only, bounded, and governed by `local_index_only` safety checks.

Reviewed routes:

- `/search`
- `/api/v1/status`
- `/api/v1/search`
- `/api/v1/query-plan`
- `/api/v1/sources`
- `/api/v1/source/{source_id}`

Review findings:

- Forbidden path, URL, live probe, download, install, upload, and credential
  parameters remain blocked.
- Status reports live probes, downloads, installs, uploads, local paths, and
  telemetry disabled.
- Public-alpha smoke remains a local check and is not deployment evidence.
- No private path leakage was observed in the public search rehearsal report.

Public-alpha is still not a hosted production posture.
