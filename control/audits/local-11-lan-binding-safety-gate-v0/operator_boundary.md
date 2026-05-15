# Operator Boundary

Operator-gated mutations stay localhost-only.

The following routes remain loopback/token-gated:

- `POST /review/<review_item_id>/decision`
- `POST /rebuild`

The raw operator token is never exposed to LAN clients and is not logged by the
LAN policy check.
