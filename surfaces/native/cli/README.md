# Native CLI Surface

`surfaces/native/cli/` is the first non-web Eureka surface family proof.

This bootstrap CLI:

- stays on the public side of the architecture
- uses `runtime/gateway/public_api/` plus shared surface-neutral mappings
- remains local, deterministic, stdlib-only, and bounded
- shows bounded source-family and source-origin summaries for synthetic fixtures and recorded GitHub Releases-backed results
- does not settle the long-term CLI, TUI, or native-shell architecture

Commands currently exposed:

- `resolve <target_ref>`
- `search <query>`
- `export-manifest <target_ref>`
- `export-bundle <target_ref>`
- `inspect-bundle <path>`
- `store-manifest <target_ref> --store-root <path>`
- `store-bundle <target_ref> --store-root <path>`
- `list-stored <target_ref> --store-root <path>`
- `read-stored <artifact_id> --store-root <path>`

Each command defaults to readable plain text and accepts `--json` for bounded structured output.
