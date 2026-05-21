# F0 Member Manifest

An F0 MemberManifest records a fixture-only and manifest-only view of a fixture container. It stores the container id, fixture id, member count, declared sizes, max depth, member records, risk report id, and non-claims.

Every member record includes raw and normalized path, path safety, size, depth, directory/symlink/device/absolute-path flags, traversal flags, blocked state, and block reasons. The manifest is not truth and must stay review-gated.

Required boundary language:

- no downloads
- no filesystem extraction
- no execution
- no accepted evidence
- no reviewed record creation
- no index mutation

The manifest describes what the fixture directory metadata says. It does not read member contents, write extracted files, or prove provenance.
