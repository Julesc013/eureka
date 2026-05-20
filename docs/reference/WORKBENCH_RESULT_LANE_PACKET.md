# Workbench Result Lane Packet Reference

The result lane packet uses the Search Interaction `ResultLanePacket` contract and adds Workbench projection fields where needed.

Core fields:

- schema_version
- packet_type
- emitted_at
- lane_id
- lane_kind
- projection_profile
- visible
- state
- truth_level
- review_required
- source_mapping
- result_count
- result_ids
- items
- confidence
- limitations
- uncertainty
- provenance
- action_posture
- blocked_actions

Unsafe action flags default to false: can_download, can_extract, can_execute, can_call_model, and can_deploy. Public and native read-only projections also hide operator-only fields.
