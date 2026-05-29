# Public Alpha Deploy Manifest

The dry-run manifest records what a future deploy rehearsal would package. It
does not produce deploy artifacts.

Preferred initial mode:

- `static_snapshot_site`

Allowed future dry-run alternative:

- `read_only_relay_service`

Current manifest:

- inputs are committed contracts and inventory evidence
- outputs are dry-run evidence files only
- no `site/dist` write is planned or performed
- no credentials, DNS change, or provider mutation is required
