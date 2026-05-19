# Root Inventory

Allowed active roots:

| Root | Class |
| --- | --- |
| `.aide/` | control plane |
| `.github/` | automation |
| `control/` | governance |
| `contracts/` | contract authority |
| `runtime/` | product runtime |
| `surfaces/` | surface projection |
| `native/` | native client project |
| `crates/` | Rust lane |
| `site/` | static site |
| `snapshots/` | interchange artifact |
| `examples/` | examples and fixtures |
| `docs/` | human documentation |
| `tests/` | verification |
| `evals/` | evaluation |
| `tools/` | developer tooling |
| `scripts/` | thin wrappers |
| `release/` | release definition |
| `external/` | external reference |
| `archive/` | historical archive |

Classified top-level exceptions:

- `.aide.local.example/` - committed local-state template.

Classified top-level debt:

- `data/` - generated artifact debt.
- `deploy/` - release definition debt.

`native/` remains the canonical native project root. `surfaces/native/` must not
supersede it.
