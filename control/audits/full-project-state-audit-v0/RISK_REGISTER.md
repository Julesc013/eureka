# Risk Register

| Rank | Risk | Current mitigation | Next control |
| --- | --- | --- | --- |
| 1 | Public route/data contract drift | Publication inventory and static validators pass. | Public Data Contract Stability Review v0. |
| 2 | Generated artifact drift | Generator `--check` commands pass. | Generated Artifact Drift Guard v0. |
| 3 | Static site/publication mismatch | `public_site`, `site/dist`, and publication checks pass. | Add cross-artifact drift reporting. |
| 4 | External baseline fabrication | Observed count remains 0; validators enforce pending posture. | Keep manual observation human-operated. |
| 5 | Source placeholder overclaiming | Placeholder and live-disabled statuses are represented. | Continue source placeholder honesty hardening. |
| 6 | Live probe overreach | Live probe gateway candidates are disabled; wrapper live flags false. | Require explicit approval for any live probe. |
| 7 | Native implementation before approval | Readiness and WinForms plans require human approval. | Do not scaffold native projects without approval. |
| 8 | Download/install overreach | Action policy disables risky actions. | Keep implementation blocked until policy-specific milestone. |
| 9 | Privacy/path leakage | Public-alpha and privacy policy validators pass. | Review any local cache/private path changes. |
| 10 | Rust parity drift | Python structure checks pass. | Add Cargo verification when toolchain exists. |
| 11 | Cargo unavailable | Reported clearly. | Human/operator installs toolchain or runs CI with Cargo. |
| 12 | GitHub Actions deployment unverified | Artifact check passes locally only. | Human reviews Actions/Pages run. |
| 13 | Snapshot checksum/signature misunderstanding | Signature placeholder and no-key posture validated. | Add future consumer tooling plan. |
| 14 | Relay/private-data exposure | Relay implementation is not approved; no sockets. | Threat model before prototype implementation. |
| 15 | Docs/test registry drift | Operating/test metadata checks pass. | Keep metadata updated with each milestone. |
