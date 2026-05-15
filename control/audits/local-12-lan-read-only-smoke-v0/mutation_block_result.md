# Mutation Block Result

LAN mutation checks cover:

- `POST /rebuild`
- `POST /review/<review_item_id>/decision`
- `POST /workers/run`
- `POST /api/v1/source-probe`

HTTP loopback probes must reject or token-gate mutation routes. LAN-scope route
simulation must reject mutation attempts with the LAN client gate before
operator token handling.
