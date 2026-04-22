# Native CLI Surface

`surfaces/native/cli/` is the first non-web Eureka surface family proof.

This bootstrap CLI:

- stays on the public side of the architecture
- uses `runtime/gateway/public_api/` plus shared surface-neutral mappings
- remains local, deterministic, stdlib-only, and bounded
- shows bounded source-family and source-origin summaries for synthetic fixtures and recorded GitHub Releases-backed results
- shows bounded evidence summaries for exact resolution, search, inspection, and stored-export flows
- shows bounded miss explanations for exact-resolution misses and deterministic search no-result cases
- shows bounded ordered state listings for one bootstrap subject key with compact source and evidence summaries per state
- shows bounded side-by-side agreements and disagreements for exactly two compared targets while preserving evidence per side
- shows bounded known representations and access paths for one resolved target without implying final download, install, import, or restore semantics
- does not settle the long-term CLI, TUI, or native-shell architecture

Commands currently exposed:

- `resolve <target_ref>`
- `search <query>`
- `representations <target_ref>`
- `explain-resolve-miss <target_ref>`
- `explain-search-miss <query>`
- `states <subject_key>`
- `compare <left_target_ref> <right_target_ref>`
- `export-manifest <target_ref>`
- `export-bundle <target_ref>`
- `inspect-bundle <path>`
- `store-manifest <target_ref> --store-root <path>`
- `store-bundle <target_ref> --store-root <path>`
- `list-stored <target_ref> --store-root <path>`
- `read-stored <artifact_id> --store-root <path>`

Each command defaults to readable plain text and accepts `--json` for bounded structured output.
