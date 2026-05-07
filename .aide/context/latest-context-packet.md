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
- file_count: 4274
- source_snapshot_hash: `48f6f433dc886cefd19f51df3fd8a69178dbdfb0d926cd3533e915c36dc242c3`

## ROLE_COUNTS

- aide_contract: 52
- aide_policy: 31
- aide_prompt: 3
- aide_context: 4
- aide_queue: 26
- aide_evidence: 25
- test: 577
- docs: 2143
- script: 214
- config: 669
- generated: 9
- unknown: 521

## TEST_MAP

- path: `.aide/context/test-map.json`
- mapping_count: 2577
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
- chars: 1828
- approx_tokens: 457
- formal ledger: `.aide/reports/token-ledger.jsonl`
