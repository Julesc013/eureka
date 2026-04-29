# Current State

Relay Surface Design v0 exists as design, contract, inventory, validation, and
operator-policy work.

Current state:

- no relay runtime exists
- no sockets or listeners exist
- no protocol server exists
- no HTTP relay exists
- no FTP, SMB, AFP, NFS, WebDAV, Gopher, TLS translation, or protocol
  translation exists
- no native sidecar exists
- no snapshot mount exists
- no private file serving exists
- no live backend proxy exists
- no live source probe relay exists

Seed inputs exist:

- static public data under `public_site/data/`
- static text and file-tree seed surfaces under `public_site/text/` and
  `public_site/files/`
- a seed static snapshot under `snapshots/examples/static_snapshot_v0/`

Policy dependencies exist:

- Signed Snapshot Format v0
- Signed Snapshot Consumer Contract v0
- Native Action / Download / Install Policy v0
- Native Local Cache / Privacy Policy v0
- Relay Surface Design v0
- Native Client Contract v0

Native clients remain future. Live backend and live probe behavior remain
future/disabled. Relay implementation requires explicit human approval later.
