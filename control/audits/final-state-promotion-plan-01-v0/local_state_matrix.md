# LOCAL State Matrix

|capability_id|status|implemented|tested|runnable_now|validator|smoke_command|
|---|---|---|---|---|---|---|
|explicit_instance_root|pass_with_warnings|True|True|True|python scripts/validate_local_instance_bootstrap.py||
|instance_schema_and_migration_guard|pass_with_warnings|True|True|True|python scripts/validate_local_instance_migration_guard.py||
|runtime_composition_boundary|pass_with_warnings|True|True|True|python scripts/validate_local_runtime_composition.py||
|read_only_localhost_service|pass_with_warnings|True|True|True|python scripts/validate_local_http_service.py|python scripts/eureka_local_service_smoke.py --base-url http://127.0.0.1:8765 --json|
|html_workbench|pass_with_warnings|True|True|True|python scripts/validate_local_html_workbench.py|python scripts/eureka_local_workbench_smoke.py --base-url http://127.0.0.1:8765 --json|
|hardened_status_object_source_absence_pages|pass_with_warnings|True|True|True|python scripts/validate_local_workbench_page_hardening.py||
|workunit_queue|pass_with_warnings|True|True|True|python scripts/validate_workunit_queue.py||
|review_decision_loop|pass_with_warnings|True|True|True|python scripts/validate_local_review_rebuild.py||
|reviewed_index_rebuild|pass_with_warnings|True|True|True|python scripts/validate_local_review_rebuild.py||
|deterministic_worker_runner|pass_with_warnings|True|True|True|python scripts/validate_local_worker_runner.py||
|auto_test_auto_search_harness|pass_with_warnings|True|True|True|python scripts/validate_local_auto_test_harness.py|python scripts/eureka_local_auto_test.py --base-url http://127.0.0.1:8765 --json; python scripts/eureka_local_auto_search.py --base-url http://127.0.0.1:8765 --json|
|lan_binding_safety_gate|pass_with_warnings|True|True|True|python scripts/validate_local_lan_safety_gate.py||
|lan_read_only_smoke|pass_with_warnings|True|True|True|python scripts/validate_local_lan_smoke.py|python scripts/eureka_lan_smoke.py --instance ./eureka-instance --host 0.0.0.0 --port 8765 --bind-lan --read-only --json|
|clean_machine_bootstrap|pass_with_warnings|True|True|True|python scripts/validate_clean_machine_bootstrap.py|python scripts/eureka_clean_machine_bootstrap.py --repo . --json|
|local_closeout|pass_with_warnings|True|True|False|python scripts/validate_local_appliance_closeout.py||
|local_total_remediation|pass_with_warnings|True|True|False|python scripts/validate_runtime_architecture_leakage.py||
|local_main_promotion|pass|True|True|False|git rev-list --left-right --count origin/main...origin/dev||
