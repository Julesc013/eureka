# Legacy Software Query Set

The legacy software seed batch uses sixteen curated queries spanning portable
utilities, offline installers, driver/support media, redistributables, and old
platform-compatible applications.

The canonical matrix is:

```text
control/inventory/seed_batch_legacy_software_query_matrix.json
```

Queries are assigned `legacy_software` or `driver_support_media` domains and
carry suppressions for unsafe or irrelevant software-search noise.
