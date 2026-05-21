# Safe Fixture Inventory

The committed F0 fixture set includes one tiny safe ZIP and descriptor-only unsafe/pathological examples.

- `safe_zip_basic`
- `safe_zip_nested_directory`
- `unsafe_zip_path_traversal_manifest_fixture`
- `unsafe_zip_absolute_path_manifest_fixture`
- `large_member_declared_size_manifest_fixture`
- `future_iso_blocked_fixture_descriptor`
- `future_archive_member_query_fixture`

Unsafe cases are represented as JSON descriptors rather than dangerous archives.
