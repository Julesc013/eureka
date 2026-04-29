# Allowed Initial Features

Allowed future skeleton features, after explicit human approval:

- Create a minimal WinForms shell for `windows_7_x64_winforms_net48`.
- Display static app title and non-production status.
- Read selected repo-local static public data files by explicit relative paths.
- Read selected seed snapshot metadata by explicit relative paths.
- Display public source summary counts.
- Display public eval summary counts.
- Display a static demo query list from committed demo snapshot JSON.
- Display limitations and disabled capability status.
- Display an evidence/provenance placeholder panel.
- Fail closed when allowed input files are missing.

All allowed features must be read-only and demo-only. They must not require
network access, live backend routes, live probes, local cache, private user
data, downloads, installers, or Rust FFI.

