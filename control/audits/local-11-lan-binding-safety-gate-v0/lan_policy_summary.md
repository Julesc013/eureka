# LAN Policy Summary

LOCAL-11 keeps `127.0.0.1` as the default bind host.

LAN bind hosts are accepted only when `--bind-lan` is explicit:

- `0.0.0.0`
- `::`

LAN mode is read-only by policy. It is local network inspection of status,
search, object, source, absence, and health pages/API routes. It is not public
hosting, production readiness, public launch readiness, deployment, source
probing, WorkUnit execution, or review/rebuild mutation from LAN clients.
