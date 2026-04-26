# Native CLI Surface

`surfaces/native/cli/` is the first non-web Eureka surface family proof.

This bootstrap CLI:

- stays on the public side of the architecture
- uses `runtime/gateway/public_api/` plus shared surface-neutral mappings
- remains local, deterministic, stdlib-only, and bounded
- shows bounded source-family and source-origin summaries for synthetic fixtures and recorded GitHub Releases-backed results
- shows bounded source-family and source-origin summaries for recorded Internet Archive-like fixtures and committed local bundle fixtures without implying live Internet Archive access or arbitrary local filesystem ingestion
- shows bounded evidence summaries for exact resolution, search, inspection, and stored-export flows
- shows bounded miss explanations for exact-resolution misses and deterministic search no-result cases
- shows bounded ordered state listings for one bootstrap subject key with compact source and evidence summaries per state
- shows bounded side-by-side agreements and disagreements for exactly two compared targets while preserving evidence per side
- shows bounded source-registry listings and source detail over the public side of the architecture, including capability summaries, coverage depth, connector mode, current limitations, and next coverage steps while clearly distinguishing active fixture-backed, active recorded-fixture-backed, placeholder, and future records
- shows bounded deterministic query-plan summaries over the public side of the architecture, including old-platform platform constraints, latest-compatible intent, driver/hardware hints, vague identity uncertainty, documentation intent, member-discovery hints, and suppression hints without implying LLM planning, vector search, fuzzy retrieval, ranking, or live source behavior
- shows bounded local-index build, status, and query results over the public side of the architecture, clearly distinguishing SQLite FTS5 mode from deterministic fallback mode without implying ranking, fuzzy retrieval, vector search, live sync, or incremental indexing
- shows deterministic `synthetic_member` results from committed local bundle fixtures, including member path, parent target ref, member kind, and action hints where the public boundary provides them
- shows Archive Resolution Eval Runner v0 suite summaries over the public side of the architecture, clearly distinguishing planner satisfaction, absence partials, not-yet-evaluable checks, and capability gaps without implying ranking, fuzzy retrieval, vector search, LLM planning, crawling, live sync, or production relevance evaluation
- shows bounded synchronous local-task creation, listing, and inspection over the public side of the architecture, clearly distinguishing completed, blocked, and failed bootstrap local task records without implying background scheduling, retries, priorities, or distributed queue behavior
- shows bounded synchronous resolution-run listings and detail over the public side of the architecture, clearly distinguishing completed exact-resolution, deterministic-search, and planned-search investigation records from any future worker, full planner, or streaming semantics
- shows explicit local resolution-memory creation, listing, and inspection over the public side of the architecture, clearly distinguishing successful-resolution, successful-search, and absence-finding memory records derived from persisted runs without implying shared/cloud memory, private user-history tracking, personalization, ranking, or automatic invalidation
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
- `query-plan <raw_query>`
- `evals-archive-resolution [--task <task_id>] [--index-path <path>]`
- `index-build --index-path <path>`
- `index-status --index-path <path>`
- `index-query <query> --index-path <path>`
- `task-run <task_kind> --task-store-root <path> [--index-path <path>] [--query <query>]`
- `task-status <task_id> --task-store-root <path>`
- `tasks --task-store-root <path>`
- `run-resolve <target_ref> --run-store-root <path>`
- `run-search <query> --run-store-root <path>`
- `run-planned-search <raw_query> --run-store-root <path>`
- `run-status <run_id> --run-store-root <path>`
- `runs --run-store-root <path>`
- `memory-create --run-store-root <path> --memory-store-root <path> --run-id <run_id>`
- `memory <memory_id> --memory-store-root <path>`
- `memories --memory-store-root <path> [--kind <memory_kind>] [--run-id <run_id>] [--task-kind <task_kind>] [--source-id <source_id>]`
- `sources [--status <status>] [--family <family>] [--role <role>] [--surface <surface>] [--coverage-depth <depth>] [--capability <name>] [--connector-mode <mode>]`
- `source <source_id>`
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

`--run-store-root` is a bootstrap local persistence input only. It does not imply
async run execution, worker queues, multi-user hosting semantics, or a final
resolution-run storage contract. Planned-search commands persist a bounded
`resolution_task` summary, but they do not imply full investigation planning or
planner-driven retrieval yet.

`--index-path` is a bootstrap local SQLite path only. It does not imply a final
hosted search service, multi-user index store, background indexing, ranking,
fuzzy retrieval, vector search, or planner-owned routing behavior.

The archive-resolution eval command is an executable regression guardrail over
the current hard-query packet. Many tasks currently report `capability_gap`.
That is expected, and the command is not a ranking, semantic, fuzzy, vector,
LLM, crawling, live-sync, or production relevance benchmark.

Real Source Coverage Pack v0 broadens the local demo corpus with two recorded
fixture families: `internet-archive-recorded-fixtures` and
`local-bundle-fixtures`. CLI source and search commands may show those records,
but they are committed fixture data only, not live API access, scraping,
crawling, or arbitrary local-path ingestion.

Member-Level Synthetic Records v0 makes selected committed local-bundle members
visible as deterministic member target refs in search, local-index, and exact
resolution output. This is fixture-derived member visibility only; it is not
ranking, broad extraction, arbitrary local filesystem ingestion, or a new
connector.

`--task-store-root` is a bootstrap local persistence input only. It does not
imply background scheduling, retries, priorities, worker daemons, distributed
queues, or a final task-storage contract.

`--memory-store-root` is a bootstrap local persistence input only. It does not
imply shared/cloud memory, private user-history tracking, personalization,
ranking, automatic invalidation, or a final multi-user memory-storage contract.
