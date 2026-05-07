# AIDE Cache Key Report

## CACHE_KEYS

- schema_version: q18.cache-keys.v0
- generated_by: aide-lite q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- raw_prompt_storage: false
- raw_response_storage: false
- git_commit: cdbbc9a038dc06ef0c2b11dc11625eb5f78fa9bc
- dirty_state: true

## LOCAL_STATE_BOUNDARY

- committed_contract_root: .aide/
- local_state_root: .aide.local/
- local_state_ignored: true
- tracked_local_state_paths: 0

## SURFACES

- latest_context_packet: `.aide/context/latest-context-packet.md`
  - surface: context_packet
  - key_id: aide-cache-v0:context_packet:3a2a5bdba644e98d
  - content_sha256: cfe2c08bccd34f8f850a088c9670bb2014c4bd30c0a6f4595331745776cbb261
  - dependency_count: 6
  - dirty_state: true
- latest_golden_tasks_report: `.aide/evals/runs/latest-golden-tasks.json`
  - surface: golden_tasks_report
  - key_id: aide-cache-v0:golden_tasks_report:9c7a27a7006cb99a
  - content_sha256: e96ff1a03512e8cdc5da9a0c344e6143ee82b1cea5bd91ceb435a52469c53aba
  - dependency_count: 2
  - dirty_state: true
- latest_review_packet: `.aide/context/latest-review-packet.md`
  - surface: review_packet
  - key_id: aide-cache-v0:review_packet:e8f49632a0a59a70
  - content_sha256: ec16cc8754a8ed90035132a9b601e8880f7c348a71baf5b6ac2232ec80200769
  - dependency_count: 4
  - dirty_state: true
- latest_route_decision: `.aide/routing/latest-route-decision.json`
  - surface: route_decision
  - key_id: aide-cache-v0:route_decision:f020bb885d7addba
  - content_sha256: 0250c0c9203c8f5d9754b20a1ff7c862957fab36bec3738cc95fda33c25e6077
  - dependency_count: 6
  - dirty_state: true
- latest_task_packet: `.aide/context/latest-task-packet.md`
  - surface: task_packet
  - key_id: aide-cache-v0:task_packet:da14b8448111cf82
  - content_sha256: 45bb0e0f759fa96794c987b049ec0d87c92e6e1f2188d79f1ade272ba4f8c93a
  - dependency_count: 5
  - dirty_state: true
- latest_verification_report: `.aide/verification/latest-verification-report.md`
  - surface: verification_report
  - key_id: aide-cache-v0:verification_report:6c0a373ceaa8fe20
  - content_sha256: e02efda6c51c5387f6e1515a27f71f6a6e461a4c9747165d07aab9b3b93b8f5d
  - dependency_count: 4
  - dirty_state: true
- token_savings_summary: `.aide/reports/token-savings-summary.md`
  - surface: token_savings_summary
  - key_id: aide-cache-v0:token_savings_summary:ec56853878202d1e
  - content_sha256: c504cf198e4a8ff17051e3ffe5c6bc9987c932943862f40a7f9332d58dff33c5
  - dependency_count: 3
  - dirty_state: true

## LIMITS

- Cache keys are deterministic metadata, not permission to reuse stale or unsafe content.
- Cache hits must not bypass verifier, review gates, or golden tasks.
- Provider response and semantic caches remain disabled until future reviewed policy enables them.
- Raw prompts, raw responses, secrets, traces, and real cache blobs must stay out of committed files.
