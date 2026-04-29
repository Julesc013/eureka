# Relay Prototype Planning v0

Relay Prototype Planning v0 defines the first possible future relay prototype.
It is planning only.

Decision:

- Recommended first prototype: `local_static_http_relay_prototype`
- First protocol candidate: local static HTTP
- Default bind scope for a future implementation: localhost only
- Mode: read-only
- Inputs: allowlisted static public data, text/files seed surfaces, and the
  seed static snapshot
- Outputs: read-only pages, text, JSON summaries, file-tree indexes, checksum
  files, and snapshot manifest views

This pack does not implement a relay server, open sockets, add HTTP relay
behavior, add FTP/SMB/AFP/NFS/WebDAV/Gopher support, proxy a live backend,
mount snapshots, serve private files, expose a native sidecar, or enable live
source probes.

Future implementation requires explicit human approval.
