# AIDE Latest Context Packet

## CONTEXT_COMPILER

- compiler: q11-context-compiler-v0
- generator: aide-lite
- generator_version: q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- method: deterministic repo-local metadata, roles, priorities, and test heuristics

## SOURCE_REFS

- `.aide/context/compiler.yaml`
- `.aide/context/priority.yaml`
- `.aide/context/excerpt-policy.yaml`
- `.aide/context/ignore.yaml`
- `.aide/context/repo-snapshot.json`
- `.aide/context/context-index.json`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`

## REPO_MAP

- json: `.aide/context/repo-map.json`
- markdown: `.aide/context/repo-map.md`
- file_count: 15483
- source_snapshot_hash: `30dc9d2e5177211b9439dea1f6af8aabb64a0efe4b32f75f46ae73c4ed3d7984`

## ROLE_COUNTS

- aide_contract: 56
- aide_policy: 37
- aide_prompt: 6
- aide_context: 4
- aide_queue: 142
- aide_evidence: 90
- test: 958
- docs: 4829
- script: 637
- config: 7352
- generated: 9
- unknown: 1363

## TEST_MAP

- path: `.aide/context/test-map.json`
- mapping_count: 5882
- mappings_with_existing_candidate: 1
- complete_coverage_claimed: false

## CURRENT_QUEUE

- current_queue_ref: `.aide/queue/index.yaml`
- queue_index: `.aide/queue/index.yaml`

## EXACT_REFS

- Preferred syntax: `path#Lstart-Lend`
- Validate refs before use.
- Do not inline whole files by default.
- Never inline ignored files, secrets, local state, caches, or binary artifacts.

## PACKET_GUIDANCE

- Use repo-map and test-map refs before broad documentation dumps.
- Include exact line refs only when required for correctness.
- Ask for additional context only when the compact packet is insufficient.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 1832
- approx_tokens: 458
- formal ledger: `.aide/reports/token-ledger.jsonl`
