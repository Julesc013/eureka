# DOMAIN Pack Record

`contracts/domain/domain_pack.v0.json` defines the seed-pack record. The required
fields are:

- `domain_id`
- `display_name`
- `domain_version`
- `object_families`
- `query_classes`
- `identity_rules`
- `query_hints`
- `source_preferences`
- `result_lane_expectations`
- `suppression_rules`
- `promote_rules`
- `action_posture_defaults`
- `risk_posture_defaults`
- `rights_posture_defaults`
- `safety_posture_defaults`
- `syn_case_refs`
- `search_need_seed_policy`
- `workunit_seed_policy`
- `non_claims`
- `created_at`

The record is not truth. It carries hints, expected lanes, and blocked action
posture only. It does not create evidence, reviewed records, source probes,
downloads, extraction, model/provider calls, deployment, production readiness, or
public launch readiness. The no live source boundary is part of the record
contract.

Unsafe actions remain blocked by default. Read-only actions such as inspect,
cite, and metadata export are meaningful only where reviewed evidence exists in
other governed stores.
