# Security Boundary

Explore is private local operator UI.

- LAN requests to `/explore` are rejected.
- POST routes require an operator token.
- No live providers or network calls are enabled.
- No public Workbench is exposed.
- No review decisions, reviewed records, reviewed/master index writes, public-index writes, or snapshots are created.
- Caller-provided filesystem paths are not accepted by the route layer.

