# Pack Contracts

`contracts/packs/` defines governed portable bundle formats for future
extension and contribution workflows.

Current pack contracts are contract and validation assets only. They do not
implement import, indexing, upload, executable plugins, live connectors, hosted
submission, or master-index acceptance.

## Current Contracts

- `source_pack.v0.json` - manifest schema for Source Pack Contract v0. Source
  packs carry source metadata, public-safe evidence inputs, tiny deterministic
  fixtures, rights/privacy notes, and checksum declarations.

Future pack contracts are expected for evidence packs, index packs,
contribution packs, and review queues. Those future contracts must stay
separate from source-pack validation so one pack type cannot silently gain the
authority of another.
