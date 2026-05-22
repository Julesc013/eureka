# IA Live Metadata Lane Events

Required event types:

- `ia_live_metadata.requested`
- `ia_live_metadata.policy_checked`
- `ia_live_metadata.approved`
- `ia_live_metadata.blocked`
- `ia_live_metadata.started`
- `ia_live_metadata.request_succeeded`
- `ia_live_metadata.request_failed`
- `ia_live_metadata.rate_limited`
- `ia_live_metadata.tls_failed`
- `ia_live_metadata.normalized`
- `ia_live_metadata.candidates_projected`
- `ia_live_metadata.completed`
- `ia_live_metadata.cancelled`

Events must not include raw response bodies, operator tokens, or private local
state. They are operational breadcrumbs, not evidence.
