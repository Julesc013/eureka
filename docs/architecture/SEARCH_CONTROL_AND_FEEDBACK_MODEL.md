# Search Control And Feedback Model

Controls include pause, resume, cancel, deepen, narrow, broaden, refine_query, add_constraint, remove_constraint, include_source, exclude_source, prefer_source, suppress_source, inspect_candidate, accept_candidate_for_review, reject_candidate, mark_near_miss, mark_duplicate, mark_policy_blocked, request_more_evidence, export_resolution_packet, save_search, and watch_need.

Feedback examples include right_app_wrong_version, right_era_wrong_platform, wrong_object_family, ignore_isos, only_portable_apps, search_deeper_inside_bundles, source_relevant, source_not_relevant, file_path_promising, and needs_manual_review.

Feedback modifies the current run through SearchPlanPatch. It does not erase prior evidence. It is auditable. It may seed SearchNeed or WorkUnit later. It does not mutate the master index and it is not truth.
