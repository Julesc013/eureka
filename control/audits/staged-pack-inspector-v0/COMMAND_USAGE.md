# Command Usage

List committed synthetic examples:

```bash
python scripts/inspect_staged_pack.py --list-examples
```

Inspect all examples:

```bash
python scripts/inspect_staged_pack.py --all-examples
python scripts/inspect_staged_pack.py --all-examples --json
```

Inspect one file or root:

```bash
python scripts/inspect_staged_pack.py --manifest examples/local_staging_manifests/minimal_local_staging_manifest_v0/LOCAL_STAGING_MANIFEST.json
python scripts/inspect_staged_pack.py --manifest-root examples/local_staging_manifests/minimal_local_staging_manifest_v0
```

`--strict` passes strict validation to the manifest validator. `--no-validate`
is for diagnostic inspection only; future actions must validate first.

All modes are stdout-only. The inspector writes no files and creates no hidden
state.
