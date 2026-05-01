# Language And Runtime Strategy

| Lane | Classification | Strategy |
|---|---|---|
| Python | `implemented_runtime` | Active oracle/reference backend, validators, scripts, evals, local public search, and local prototype runtime. |
| Rust | `planning_only` | Future production/parity lane only; isolated parity candidates are not runtime wiring. |
| HTML/CSS | `implemented_static_artifact` | Static/no-JS compatibility baseline through `site/dist`, lite/text/files, and demos. |
| JavaScript/TypeScript | `deferred` | Future progressive enhancement only. |
| C#/.NET | `approval_gated` | Future Windows 7+ native client lane after explicit approval. |
| C/C++/Obj-C/etc | `deferred` | Future deep legacy clients only. |
| Ruby/PHP | `deferred` | Not core unless a specific integration justifies them. |
| AI providers | `approval_gated` | Provider-optional and never authority. |

Doctrine:

- Contracts are canonical.
- Python is the oracle.
- Rust is the future production core only after parity.
- Static HTML/CSS is the compatibility baseline.
- Native clients use the best language for their target.
- AI is optional candidate-generation support, not truth, rights clearance,
  malware safety, source trust, ranking authority, or master-index acceptance.
