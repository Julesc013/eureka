# Risk Register

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Native project starts before public data and snapshot contracts stabilize | medium | Limit first skeleton to static public data and seed snapshot inspection; no API stability claim. |
| Install/download automation pressure appears too early | high | Keep action policy gates in the skeleton brief; no download, installer, execute, mirror, or package-manager behavior. |
| Executable trust is overclaimed | high | Require executable-risk warnings; hashes identify bits but do not prove safety. |
| Local path or private data leaks into public reports | high | Apply local cache/privacy policy; no private paths in public reports, snapshots, or relay views. |
| Telemetry/account features creep into native project | high | Keep telemetry/accounts/cloud sync absent until explicit policy and user opt-in exist. |
| Old platform toolchain uncertainty blocks legacy lanes | medium | Start with Windows 7 x64 only; treat XP/Win95/Mac lanes as lab-verify or research. |
| Rust/Python mismatch appears in native expectations | medium | Native skeleton must consume public contracts/snapshots, not Rust internals. |
| Snapshot consumer is mistaken for implemented runtime | medium | Document that consumer contract exists, but no native reader runtime exists yet. |
| Relay design is mistaken for implemented relay | medium | Keep relay optional/future; no sidecar, sockets, protocol server, or LAN service. |
| UI diverges from evidence model | medium | Require evidence/provenance display and preserve uncertainty in every result card. |
| API/public-data compatibility drifts | medium | Use validators and generated public data checks before any native milestone. |
| Users expect app-store or installer behavior | high | Label first skeleton as read-only inspection only, with no install/download affordances. |

