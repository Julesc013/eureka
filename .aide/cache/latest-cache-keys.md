# AIDE Cache Key Report

## CACHE_KEYS

- schema_version: q18.cache-keys.v0
- generated_by: aide-lite q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- raw_prompt_storage: false
- raw_response_storage: false
- git_commit: 0d283f5879e509d297e4be99dbdaf045db851ecb
- dirty_state: true

## LOCAL_STATE_BOUNDARY

- committed_contract_root: .aide/
- local_state_root: .aide.local/
- local_state_ignored: true
- tracked_local_state_paths: 0

## SURFACES

- latest_context_packet: `.aide/context/latest-context-packet.md`
  - surface: context_packet
  - key_id: aide-cache-v0:context_packet:0d562094b94eebf0
  - content_sha256: 5c26b329e947f1d003c8c74c3277d2e4fc02f4522ba701f5be9f6a006d9d5373
  - dependency_count: 6
  - dirty_state: true
- latest_golden_tasks_report: `.aide/evals/runs/latest-golden-tasks.json`
  - surface: golden_tasks_report
  - key_id: aide-cache-v0:golden_tasks_report:e1de3dc3042d6fd9
  - content_sha256: db1fb389730cc87bd2a54020f536b4074eedb2ef16d24c5887cdcd14b6127326
  - dependency_count: 2
  - dirty_state: true
- latest_review_packet: `.aide/context/latest-review-packet.md`
  - surface: review_packet
  - key_id: aide-cache-v0:review_packet:472c132816e00707
  - content_sha256: 57a3bf4a2534db8f67a62efaec94dd44365a2fa74480da5d188764c903e2cd6f
  - dependency_count: 4
  - dirty_state: true
- latest_route_decision: `.aide/routing/latest-route-decision.json`
  - surface: route_decision
  - key_id: aide-cache-v0:route_decision:75165c852610f2d7
  - content_sha256: 0250c0c9203c8f5d9754b20a1ff7c862957fab36bec3738cc95fda33c25e6077
  - dependency_count: 6
  - dirty_state: true
- latest_task_packet: `.aide/context/latest-task-packet.md`
  - surface: task_packet
  - key_id: aide-cache-v0:task_packet:2109176d1d18d8b0
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
  - key_id: aide-cache-v0:token_savings_summary:c6cab78a862c7aab
  - content_sha256: daa20860cf955036c347cf990c3fc37f4cb73ccce01f669ace2e7a016e0533e0
  - dependency_count: 3
  - dirty_state: true

## LIMITS

- Cache keys are deterministic metadata, not permission to reuse stale or unsafe content.
- Cache hits must not bypass verifier, review gates, or golden tasks.
- Provider response and semantic caches remain disabled until future reviewed policy enables them.
- Raw prompts, raw responses, secrets, traces, and real cache blobs must stay out of committed files.
