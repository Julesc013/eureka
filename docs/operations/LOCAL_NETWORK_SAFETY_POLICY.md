# Local Network Safety Policy

Eureka is localhost-first. LAN binding is disabled by default and requires an explicit future flag.

LAN mode defaults to read-only. Write actions require a local operator token. Unauthenticated LAN clients may not mutate sources, review decisions, WorkUnits, indexes, or config. LAN closeout requires a shutdown or rollback command and a firewall/operator warning.

LOCAL-00 does not expose LAN and does not implement the HTTP service.
