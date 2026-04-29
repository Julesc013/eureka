# Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Planning is mistaken for permission to create a native project | high | Keep human approval gate explicit; validator rejects project files. |
| Skeleton grows into prototype behavior | high | Restrict initial scope to read-only public data and seed snapshot display. |
| Download/install controls appear early | high | Keep action policy prohibitions in scope and test for project-file drift. |
| Private paths or local scans enter native code | high | Require explicit relative inputs and prohibit arbitrary filesystem scanning. |
| Toolchain compatibility is assumed | medium | Require Windows host, VS 2022, .NET Framework 4.8 developer pack, and x64 target verification before implementation. |
| UI implies executable safety or rights clearance | high | Require limitation/status panels and evidence/provenance wording. |
| Rust parity work is mistaken for native SDK readiness | medium | Prohibit Rust FFI and runtime replacement in the skeleton. |
| Live backend/probe behavior slips in | high | No network by default and no live backend dependency. |
| Repo boundary gets blurry | medium | Keep future project under `clients/`, not runtime, gateway, or existing surfaces. |

