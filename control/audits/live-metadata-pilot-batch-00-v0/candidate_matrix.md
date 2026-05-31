# Candidate Matrix

```json
{
  "accepted_truth": false,
  "accepted_truth_created": false,
  "candidate_count": 8,
  "candidate_index_handoff_created": true,
  "candidate_index_mutated": false,
  "candidate_refs": [
    "live_metadata_pilot_frontier_media_q01_01",
    "live_metadata_pilot_frontier_media_q03_02",
    "live_metadata_pilot_frontier_media_q05_03",
    "live_metadata_pilot_frontier_media_q06_04",
    "live_metadata_pilot_legacy_software_q01_05",
    "live_metadata_pilot_legacy_software_q02_06",
    "live_metadata_pilot_legacy_software_q03_07",
    "live_metadata_pilot_legacy_software_q06_08"
  ],
  "candidates": [
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_frontier_media_q01_01",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "ae7df5388d35bfd849912c3f",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "frontier_resolution_media",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_frontier_media_q01_01",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "ae7df5388d35bfd849912c3f",
        "domain_id": "frontier_resolution_media",
        "fingerprint_id": "candidate-fingerprint:ae7df5388d35bfd849912c3f",
        "normalized_title": "redacted live ia metadata summary for new york 1993 d-theater hd demo tape original source",
        "object_hint": "redacted live ia metadata summary for new york 1993 d-theater hd demo tape original source",
        "platform_hint": "d-theater",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"f73ee8216e536feb\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:2ee1238a44c933bb\"}",
        "version_hint": "1993"
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "New York 1993 D-Theater HD demo tape original source",
      "query_plan_ref": "seed_query_plan:d4a8f229c25b08e8",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:ada86b1d33e1b377",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "f73ee8216e536feb",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:2ee1238a44c933bb"
      },
      "source_observation_ref": "live_metadata_source_observation:efc74d7dbc7eff8b",
      "suppressions": [
        "suppress_generic_city_or_tourism_media"
      ],
      "title": "Redacted live IA metadata summary for New York 1993 D-Theater HD demo tape original source",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_frontier_media_q03_02",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "1585ce4440e2a40fce9250e8",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "frontier_resolution_media",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_frontier_media_q03_02",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "1585ce4440e2a40fce9250e8",
        "domain_id": "frontier_resolution_media",
        "fingerprint_id": "candidate-fingerprint:1585ce4440e2a40fce9250e8",
        "normalized_title": "redacted live ia metadata summary for jvc d-theater new york hd demo",
        "object_hint": "redacted live ia metadata summary for jvc d-theater new york hd demo",
        "platform_hint": "d-theater",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"664edb11ce00d6d8\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:0ac41bb5e1e9a32a\"}",
        "version_hint": ""
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "JVC D-Theater New York HD demo",
      "query_plan_ref": "seed_query_plan:1f71a1830d1d1c25",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:33780a7df55b5f29",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "664edb11ce00d6d8",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:0ac41bb5e1e9a32a"
      },
      "source_observation_ref": "live_metadata_source_observation:aa933bbd7ad9d765",
      "suppressions": [
        "suppress_generic_city_or_tourism_media"
      ],
      "title": "Redacted live IA metadata summary for JVC D-Theater New York HD demo",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_frontier_media_q05_03",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "0bc02e0407e37ab321de0674",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "frontier_resolution_media",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_frontier_media_q05_03",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "0bc02e0407e37ab321de0674",
        "domain_id": "frontier_resolution_media",
        "fingerprint_id": "candidate-fingerprint:0bc02e0407e37ab321de0674",
        "normalized_title": "redacted live ia metadata summary for hi-vision muse new york 1993 hdtv demo",
        "object_hint": "redacted live ia metadata summary for hi-vision muse new york 1993 hdtv demo",
        "platform_hint": "",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"f73ee8216e536feb\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:de91338c0be8faa8\"}",
        "version_hint": "1993"
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "Hi-Vision MUSE New York 1993 HDTV demo",
      "query_plan_ref": "seed_query_plan:3c12f38bb56f962d",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:a4b2e6c5f0bf4adf",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "f73ee8216e536feb",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:de91338c0be8faa8"
      },
      "source_observation_ref": "live_metadata_source_observation:eba7e261f2b6befa",
      "suppressions": [
        "suppress_generic_city_or_tourism_media"
      ],
      "title": "Redacted live IA metadata summary for Hi-Vision MUSE New York 1993 HDTV demo",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_frontier_media_q06_04",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "27637c0e2e5cf06148fa1c64",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "frontier_resolution_media",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_frontier_media_q06_04",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "27637c0e2e5cf06148fa1c64",
        "domain_id": "frontier_resolution_media",
        "fingerprint_id": "candidate-fingerprint:27637c0e2e5cf06148fa1c64",
        "normalized_title": "redacted live ia metadata summary for early hdtv new york 1993 demo footage",
        "object_hint": "redacted live ia metadata summary for early hdtv new york 1993 demo footage",
        "platform_hint": "",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"ce88ebfa1edab05c\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:329a4cdef5174e42\"}",
        "version_hint": "1993"
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "early HDTV New York 1993 demo footage",
      "query_plan_ref": "seed_query_plan:3fee564222e22091",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:a514e75ddc45a851",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "ce88ebfa1edab05c",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:329a4cdef5174e42"
      },
      "source_observation_ref": "live_metadata_source_observation:e42957553d3edf79",
      "suppressions": [
        "suppress_generic_city_or_tourism_media",
        "suppress_modern_hd_stock"
      ],
      "title": "Redacted live IA metadata summary for early HDTV New York 1993 demo footage",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_legacy_software_q01_05",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "41535073d6250516bdec259d",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "legacy_software",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_legacy_software_q01_05",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "41535073d6250516bdec259d",
        "domain_id": "legacy_software",
        "fingerprint_id": "candidate-fingerprint:41535073d6250516bdec259d",
        "normalized_title": "redacted live ia metadata summary for windows 7-compatible portable utilities not windows iso",
        "object_hint": "redacted live ia metadata summary for windows 7-compatible portable utilities not windows iso",
        "platform_hint": "windows 7",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"e3364703516b5e71\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:d863f1df03bf6e31\"}",
        "version_hint": ""
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "Windows 7-compatible portable utilities, not Windows 7 ISO",
      "query_plan_ref": "legacy_seed_query_plan:e93196d42a8b499d",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:64d6dae014b1b89c",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "e3364703516b5e71",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:d863f1df03bf6e31"
      },
      "source_observation_ref": "live_metadata_source_observation:0899b4ead04957a5",
      "suppressions": [
        "generic_os_iso",
        "operating_system_image",
        "unrelated_modern_version"
      ],
      "title": "Redacted live IA metadata summary for Windows 7-compatible portable utilities, not Windows 7 ISO",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_legacy_software_q02_06",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "d34dbb93ee95ec504f8f6b8b",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "legacy_software",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_legacy_software_q02_06",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "d34dbb93ee95ec504f8f6b8b",
        "domain_id": "legacy_software",
        "fingerprint_id": "candidate-fingerprint:d34dbb93ee95ec504f8f6b8b",
        "normalized_title": "redacted live ia metadata summary for directx sdk june 2010 offline installer",
        "object_hint": "redacted live ia metadata summary for directx sdk june 2010 offline installer",
        "platform_hint": "directx",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"04631f42311aa0ca\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:3ecc6325324f5b4c\"}",
        "version_hint": "2010"
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "DirectX SDK June 2010 offline installer",
      "query_plan_ref": "legacy_seed_query_plan:596e6747763713b9",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:01de4c8cf6e758d2",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "04631f42311aa0ca",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:3ecc6325324f5b4c"
      },
      "source_observation_ref": "live_metadata_source_observation:f9a237e73d2ddb6d",
      "suppressions": [
        "web_installer_when_offline_requested",
        "wrong_version"
      ],
      "title": "Redacted live IA metadata summary for DirectX SDK June 2010 offline installer",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_legacy_software_q03_07",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "126b4bca99a588fa6c2e0460",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "driver_support_media",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_legacy_software_q03_07",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "126b4bca99a588fa6c2e0460",
        "domain_id": "driver_support_media",
        "fingerprint_id": "candidate-fingerprint:126b4bca99a588fa6c2e0460",
        "normalized_title": "redacted live ia metadata summary for stylewriter 2500 mac os driver",
        "object_hint": "redacted live ia metadata summary for stylewriter 2500 mac os driver",
        "platform_hint": "mac os 8",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"04631f42311aa0ca\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:f306403c80116097\"}",
        "version_hint": ""
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "StyleWriter 2500 Mac OS 8 driver",
      "query_plan_ref": "legacy_seed_query_plan:2b57d5c013189e89",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:0787e62587db21b0",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "04631f42311aa0ca",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:f306403c80116097"
      },
      "source_observation_ref": "live_metadata_source_observation:37a5836c2a110bbd",
      "suppressions": [
        "fake_driver_updater",
        "wrong_platform",
        "wrong_version"
      ],
      "title": "Redacted live IA metadata summary for StyleWriter 2500 Mac OS 8 driver",
      "updated_at": "2026-05-30T00:00:00Z"
    },
    {
      "accepted_truth": false,
      "action_posture": {
        "accepted_truth": false,
        "allowed_actions": [
          "inspect",
          "view_source",
          "view_provenance",
          "read"
        ],
        "blocked_actions": [
          "download",
          "install_handoff",
          "execute",
          "upload",
          "extract",
          "promote"
        ],
        "future_gated_actions": [
          "create_review_handoff",
          "update_candidate_state"
        ],
        "public_mutation_enabled": false
      },
      "candidate_id": "live_metadata_pilot_legacy_software_q06_08",
      "candidate_kind": "source_metadata_candidate",
      "confidence_label": "medium",
      "created_at": "2026-05-30T00:00:00Z",
      "dedupe_key": "f9583de73c14b81b91bfc216",
      "description": "Redacted Internet Archive metadata summary; review required before use.",
      "domain_id": "legacy_software",
      "evidence_candidate_refs": [],
      "fingerprint": {
        "candidate_id": "live_metadata_pilot_legacy_software_q06_08",
        "checksum_hint": "",
        "collision_notes": [],
        "dedupe_key": "f9583de73c14b81b91bfc216",
        "domain_id": "legacy_software",
        "fingerprint_id": "candidate-fingerprint:f9583de73c14b81b91bfc216",
        "normalized_title": "redacted live ia metadata summary for quicktime windows xp offline installer",
        "object_hint": "redacted live ia metadata summary for quicktime windows xp offline installer",
        "platform_hint": "windows xp",
        "schema_version": "candidate_fingerprint.v0",
        "source_family": "internet_archive_metadata",
        "source_locator": "{\"identifier_hash\":\"04631f42311aa0ca\",\"locator_kind\":\"redacted_archive_org_metadata_summary\",\"request_plan_id\":\"live_metadata_request_plan:6f13cfb79e2dfe62\"}",
        "version_hint": ""
      },
      "fixture_derived": false,
      "limitations": [
        "redacted_metadata_summary_only",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "no_raw_response_commit",
        "no_download",
        "no_extraction",
        "no_auto_promotion"
      ],
      "live_metadata_derived": true,
      "match_reasons": [
        "internet_archive_metadata_summary",
        "bounded_live_metadata_pilot",
        "review_required"
      ],
      "matched_query": "QuickTime 7 Windows XP offline installer",
      "query_plan_ref": "legacy_seed_query_plan:4bab156cf23bbaa4",
      "review_state": "needs_review",
      "reviewed_record_ref": null,
      "schema_version": "candidate_record.v0",
      "source_action_ref": "live_metadata_source_action:3a04228d049bc794",
      "source_family": "internet_archive_metadata",
      "source_locator": {
        "identifier_hash": "04631f42311aa0ca",
        "locator_kind": "redacted_archive_org_metadata_summary",
        "request_plan_id": "live_metadata_request_plan:6f13cfb79e2dfe62"
      },
      "source_observation_ref": "live_metadata_source_observation:c7194f99afda2bb5",
      "suppressions": [
        "web_installer_when_offline_requested",
        "wrong_platform",
        "wrong_version"
      ],
      "title": "Redacted live IA metadata summary for QuickTime 7 Windows XP offline installer",
      "updated_at": "2026-05-30T00:00:00Z"
    }
  ],
  "created_at": "2026-05-31T00:00:00Z",
  "deployment_performed": false,
  "download_performed": false,
  "extraction_executed": false,
  "master_index_mutated": false,
  "model_provider_used": false,
  "operator_instance_mutated": false,
  "pilot_batch_id": "live_metadata_pilot_batch_00",
  "production_readiness_claimed": false,
  "public_index_mutated": false,
  "public_launch_readiness_claimed": false,
  "public_live_source_fanout_enabled": false,
  "public_mutation_enabled": false,
  "raw_live_response_committed": false,
  "review_required": true,
  "reviewed_index_mutated": false,
  "schema_version": "live_metadata_pilot_candidate_matrix.v0",
  "store_mode": "pilot_redacted_summary_examples"
}
```
