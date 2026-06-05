# Legacy Shim Status

Old runtime compatibility paths remain present and appear shim-only.

| Legacy Path | Canonical Path | Contents | Last Commit | Recommendation |
|---|---|---|---|---|
| `runtime/evidence_ledger/` | `runtime/evidence/ledger/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/source_cache/` | `runtime/source/cache/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/source_observation/` | `runtime/source/observation/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/source_registry/` | `runtime/source/registry/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/search_hunt/` | `runtime/search/hunt/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/search_need/` | `runtime/search/need/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/search_quality/` | `runtime/search/quality/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |
| `runtime/workunit_queue/` | `runtime/worker/workunit_queue/` | `README.md`, `__init__.py` redirect shim | `1e0ee540` | keep shim-only |

## Rule

New implementation must go under canonical paths, not old shim paths.
