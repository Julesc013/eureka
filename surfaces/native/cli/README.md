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
- shows bounded compatibility verdicts for one resolved target against one bootstrap host profile preset without implying a final compatibility oracle, installer, or runtime-routing model
- shows bounded representation-selection and handoff recommendations for one resolved target, preserving preferred, available, unsuitable, and unknown choices without implying downloads, installers, launches, or final runtime-routing behavior
- shows bounded acquisition results for one explicitly chosen representation, optionally writing deterministic local fixture bytes to disk without implying live downloading, installers, or execution behavior
- shows bounded decomposition results for one explicitly chosen fetched representation, including compact ZIP member listings plus explicit unsupported or unavailable outcomes without implying extraction, installers, import, or restore behavior
- shows bounded member-readback results for one explicitly chosen member inside one explicitly chosen fetched representation, including compact text previews or optional local byte writes without implying extraction-to-disk by default, installers, import, or restore behavior
- shows bounded recommended, available, and unavailable next-step actions for one resolved target, optionally shaped by one bootstrap host profile preset plus one bootstrap strategy profile, without implying execution, installer, runtime-routing, or personalization behavior
- does not settle the long-term CLI, TUI, or native-shell architecture

Commands currently exposed:

- `resolve <target_ref>`
- `search <query>`
- `representations <target_ref>`
- `plan <target_ref> [--host <host_profile_id>] [--strategy <strategy_id>] [--store-root <path>]`
- `compatibility <target_ref> --host <host_profile_id>`
- `handoff <target_ref> [--host <host_profile_id>] [--strategy <strategy_id>]`
- `fetch <target_ref> --representation <representation_id> [--output <path>]`
- `decompose <target_ref> --representation <representation_id>`
- `member <target_ref> --representation <representation_id> --member <member_path> [--output <path>]`
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
