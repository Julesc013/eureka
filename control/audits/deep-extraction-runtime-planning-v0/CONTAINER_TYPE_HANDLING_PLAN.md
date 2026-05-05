# Container Type Handling Plan

All container handling is future-only and metadata-first.

- ZIP/TAR/GZIP/7z archives: metadata first; member listing only after sandbox
  approval; no payload extraction until approved.
- ISO images: metadata first; no mount, execution, install, or boot behavior.
- Disk images: metadata first; no mount, execution, emulator, or VM launch.
- Installers: risk labelled; no execution or installer inspection beyond
  metadata until approved.
- Package archives: metadata first; no install, dependency resolution, lifecycle
  script execution, or package-manager invocation.
- Python wheels/sdists: metadata first; no install or code execution.
- npm tarballs: metadata first; no npm/yarn/pnpm invocation or lifecycle scripts.
- WARC: metadata first; no replay or URL fetching.
- WACZ: metadata first; no replay or URL fetching.
- PDF: metadata first; text summary only after policy approval; no raw dumps.
- Scanned volumes: OCR hook future only; OCR runtime disabled.
- Source bundles: metadata first; no source-code safety claim.
- Repository snapshots: metadata first; no clone or live source fetch.
- Unknown containers: reject or review-required.

For every category: no execution, no install, no source-code safety claim, no
malware safety claim, and payload extraction disabled until approved.

