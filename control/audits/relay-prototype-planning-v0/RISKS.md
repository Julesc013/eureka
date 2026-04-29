# Risks

Primary risks:

- a planning document is mistaken for a working relay
- localhost scope drifts into LAN or public exposure too early
- a static relay becomes a live backend proxy
- live probe controls leak into old-client surfaces
- path traversal or generic file serving exposes private files
- logs expose private paths, credentials, or user history
- old-client transports are treated as secure
- checksum display is mistaken for authenticity
- snapshot placeholder signatures are overclaimed
- relay output becomes a download or installer surface
- future native sidecars expose private cache before privacy review
- protocol implementation starts before threat modeling

Risk posture:

- keep first prototype local-only, read-only, and static
- require explicit human approval before implementation
- require allowlisted roots and path traversal tests
- prohibit private data, writes, live probes, live backend proxying, telemetry,
  downloads, installers, and executable launch
