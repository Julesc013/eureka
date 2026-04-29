# Implementation Boundaries

This planning milestone does not implement:

- relay server
- socket listener
- HTTP relay
- FTP, SMB, AFP, NFS, WebDAV, or Gopher server
- TLS or protocol translation
- native sidecar behavior
- snapshot mounting
- private file serving
- live backend proxying
- live source probes
- arbitrary local filesystem ingestion
- account/session behavior
- telemetry
- downloads
- installers
- executable launch
- Rust runtime wiring

Future implementation should live in a new, explicitly approved path. It should
not modify current web, CLI, API, static Pages, public-alpha, Rust parity, or
engine runtime behavior without a separate approved milestone.
