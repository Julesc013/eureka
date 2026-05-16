# Planning Packet

| Field | Value |
| --- | --- |
| schema_version | hunt_perfect_planning_packet.v0 |
| task | HUNT-PERFECT-CLOSEOUT-01 |
| branch_state | `{"branch": "dev", "dev_contains_main": true, "dev_main_divergence": "0\t19", "head": "2af3514dd8fbf3a2e11661d07f12641ffab99796", "main_contains_dev": false, "origin_dev": "be9a23c6a49415fbdceafd03a68555026a77b5bf", "origin_main": "73d8e9eb5` |
| implemented_hunt_capabilities | `["hunt_00_track_plan", "hunt_01_search_hunt_session_runtime", "hunt_02_local_workbench_hunt_ui_state", "hunt_03_pause_resume_cancel_steer_commands", "hunt_04_exhaustion_reports", "hunt_05_searchneed_runtime_and_hunt_to_need_pipeline", "hunt` |
| implemented_local_dependencies | `["Local Appliance", "localhost service", "HTML workbench", "WorkUnit queue", "deterministic local workers", "local eval/report checks"]` |
| aide_state | `{"eval_green": true, "golden_fail_count": 0, "golden_pass_count": 136, "golden_task_count": 136, "report_size_clean": true, "updated_baseline_integrated": true}` |
| validation_status | `{"AIDE commit check": "pass", "AIDE doctor": "pass", "AIDE eval run": "pass", "AIDE review-pack": "pass", "AIDE selftest": "pass", "AIDE test": "pass", "AIDE validate": "pass", "AIDE verify": "pass", "HUNT AI escalation disabled-boundary de` |
| warnings | `{"remaining": 0, "state": "zero"}` |
| blockers | `{"remaining": 0, "state": "zero"}` |
| explicit_non_claims | `["not production readiness", "not public launch readiness", "not source truth", "not AI output truth", "not rights or malware clearance", "not authorization for source probes, extraction, downloads, installs, execution, scraping, crawling, ` |
| what_can_run_locally_now | `["Search Hunt sessions", "Hunt UI/API state", "operator-gated command and steering state", "exhaustion reports", "SearchNeed and WorkUnit creation", "safe deterministic background hunt workers", "deterministic replay", "AI escalation prefli` |
| what_remains_disabled | `["source probes", "extraction", "AI/model/provider execution", "agent research execution", "downloads/install/execution", "source sync", "master index mutation", "deployment", "production/public launch claims"]` |
| why_syn_is_next | SYN should create synthetic query and eval pressure over the completed Local Appliance and Search Hunt spine before extraction/source expansion. |
| why_f0_is_deferred_but_resumable | F0 can resume through HUNT/SearchNeed/WorkUnit/local eval boundaries, but extraction should wait for SYN pressure unless the operator explicitly prioritizes extraction planning. |
| promotion_recommendation | Run HUNT-TO-MAIN-PROMOTION-REVIEW before starting SYN unless the operator chooses to keep HUNT dev-only. |
| recommended_next_task | HUNT-TO-MAIN-PROMOTION-REVIEW |
| alternative_next_task | SYN-00 — Synthetic Query Foundry planning over Local Appliance |
