# Inspector Summary

Staged Pack Inspector v0 adds `scripts/inspect_staged_pack.py`.

The tool reads:

- one explicit `--manifest`
- one explicit `--manifest-root`
- all committed synthetic examples with `--all-examples`

When no explicit input is supplied, the default is all committed examples. The
tool performs read-only inspection only. It validates the manifest first unless
`--no-validate` is supplied, redacts obvious private paths and secret-like
values, and reports candidate metadata without treating staged records as
canonical truth.

The inspector is not a local staging tool, import tool, local index builder,
public-search updater, upload mechanism, or master-index submission path.
