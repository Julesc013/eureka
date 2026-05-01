# Native Relay Snapshot Status

| Area | Evidence | Classification | Notes |
|---|---|---|---|
| Static snapshot format | `generate_static_snapshot.py --check`, `validate_static_snapshot.py` | `implemented_static_artifact` | Seed snapshot example only. |
| Snapshot consumer contract | `validate_snapshot_consumer_contract.py` | `contract_only` | No consumer runtime. |
| Snapshot tooling | generator and validator | `implemented_local_prototype` | Static/offline seed only. |
| Native client contracts/plans | `validate_native_client_contract.py` | `contract_only` | No native GUI. |
| Native runtime | CLI proof only | `implemented_local_prototype` | No Visual Studio/Xcode projects. |
| Windows 7 WinForms plan | `validate_windows_winforms_skeleton_plan.py` | `approval_gated` | Requires explicit approval. |
| Relay design/prototype plan | relay validators | `planning_only` | Local static HTTP is planned first candidate. |
| Relay runtime | no sockets/protocol servers | `approval_gated` | No relay implementation. |
| Lite/text/files surfaces | `site/dist/lite`, `text`, `files` | `implemented_static_artifact` | Static compatibility surfaces. |
| Offline support | static artifact and seed snapshot | `implemented_static_artifact` | Offline reader/runtime remains future. |
