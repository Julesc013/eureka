# Local LAN Operator Boundary

Operator mutations remain localhost-only in LOCAL-11.

The operator token does not grant LAN mutation access. A LAN client requesting
`POST /review/<review_item_id>/decision` or `POST /rebuild` receives a
fail-closed rejection before token handling.

Loopback clients still follow the LOCAL-08 behavior:

- missing token is rejected
- invalid token is rejected
- valid token may record a local review decision or apply a local reviewed-index
  rebuild

LAN clients cannot use source probe, WorkUnit execution, extraction, agent,
config mutation, upload, download, install, execute, deployment, or master-index
mutation routes.

LOCAL-12 verifies this boundary with two checks:

- HTTP read-only probing against the explicit LAN-bound server.
- LAN-scope route-gate simulation for mutation attempts, which must return a
  fail-closed rejection before operator token handling.
