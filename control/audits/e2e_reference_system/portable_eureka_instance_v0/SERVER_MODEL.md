# Server Model

`serve --mode exploration` uses `runtime.local.service.route_request` through the existing local service server.

Properties:

- host default: `127.0.0.1`
- port default: `8765`
- non-loopback binds rejected
- `/explore` and `/api/v1/explore` available
- public alpha disabled
- LAN mode disabled
- live providers disabled
- token accepted or generated for process only
- token not persisted
