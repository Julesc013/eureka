# Human-Operated Work

Parallel human-operated work:

- Manual Observation Batch 0 Execution: human must perform searches and record observations manually.
- GitHub Actions/Pages run review: human/operator should inspect actual workflow run and deployed Pages state if deployment evidence is needed.
- Cargo/toolchain setup or CI review: human/operator should provide a Rust toolchain or CI evidence before claiming Cargo checks.
- Native implementation approval decision: human must explicitly approve any Visual Studio/WinForms skeleton implementation.
- Relay implementation approval decision: human must explicitly approve any relay prototype implementation, bind scope, and input roots.
- Live probe approval decision: human must explicitly approve any Internet Archive live probe or other live external source behavior.
- Hosting/operator signoff: human must approve any hosted rehearsal, DNS, custom domain, provider config, or production-facing change.

These tasks must not be automated by Codex in this milestone.
