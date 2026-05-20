# Query Compilation Model

The compiler is deterministic-first: rules, aliases, source policies, domain packs, known SearchNeeds, source cache, local reviewed index, candidate index, and WorkUnits before optional future AI suggestion.

Required compilation outputs include raw_query, normalized_query, interpreted_intent, object_family, object_kind, action_intent, target_platform, target_machine_profile, constraints, preferences, exclusions, promoted_result_types, suppressed_result_types, source_scope, depth_mode, risk_posture, rights_posture, safety_posture, confidence, clarification_needed, and user_visible_interpretation.

Example full-sentence query: I am looking for Windows 7-compatible utilities, preferably portable, not the Windows 7 ISO itself. I want things that are safe to install on an offline retro PC.

Compiled example fields: object_kind software_application; platform_constraint windows_7; preferences portable, offline_usable, low_risk; suppress operating_system_iso and unrelated_bundle_without_member_index; promote individual_installer, portable_package, compatibility_evidenced_release; safety_posture conservative.

The user-visible interpretation must be shown and correctable.
