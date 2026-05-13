# State Machine

States: queued, running, paused, blocked, complete, failed, cancelled.

Types: search_need, source_probe, evidence_review, index_rebuild, regression_test, extraction_task, agent_task.

Invalid transitions fail closed. Complete-to-complete and cancelled-to-cancelled are idempotent where practical.
