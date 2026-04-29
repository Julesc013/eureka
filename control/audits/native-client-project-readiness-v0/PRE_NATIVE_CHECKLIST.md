# Pre-Native Checklist

Status: unsigned and future.

Before any native project scaffold is created:

- [ ] Human explicitly approves native project scaffolding.
- [ ] First lane is confirmed as `windows_7_x64_winforms_net48`.
- [ ] Project path and namespace are chosen.
- [ ] Build host and toolchain are available and documented.
- [ ] Public data contract and generated summaries are reviewed.
- [ ] Snapshot consumer contract and seed snapshot format are reviewed.
- [ ] Action / Download / Install Policy is reviewed.
- [ ] Local Cache / Privacy Policy is reviewed.
- [ ] Native Client Contract and Native Client Lanes are reviewed.
- [ ] No installer automation is approved.
- [ ] No download, mirror, execute, or package-manager integration is approved.
- [ ] No private data scanning or private cache is approved.
- [ ] No telemetry, analytics, accounts, cloud sync, or diagnostic upload is approved.
- [ ] No relay sidecar, socket, or protocol server is approved.
- [ ] No live backend or live source probe dependency is approved.
- [ ] No Rust FFI or runtime replacement is approved.
- [ ] UI scope is limited to read-only public data and snapshot/evidence/status display.
- [ ] License/public contribution posture is reviewed if a new project tree is created.
- [ ] Operator signoff is recorded.

