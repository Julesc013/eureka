# Extraction Safety Guards

F-BUNDLE-01 guards include:

- Path traversal blocking for absolute paths, parent traversal, drive prefixes, and null bytes.
- Symlink and special-file blocking.
- Resource limits for input size, member count, member name length, total uncompressed bytes, and manifest bytes.
- Archive-bomb blocking by compression ratio and total uncompressed size.
- Output-root refusal for `site/dist`, `site/dist/data/public_index`, `runtime`, `contracts`, master-index roots, and local private roots.

These guards produce safety reports only. They are not malware-safety claims.
