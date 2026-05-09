# Source Coverage Model

Coverage is a bounded statement about local evidence. The model connects Source
OS source records to connector families and D0-D5 index depth:

- `D0_source_known`: source exists and policy posture is known.
- `D1_catalog_indexed`: catalog shape is represented.
- `D2_metadata_indexed`: metadata records can be normalized in fixture or dry-run mode.
- `D3_representation_indexed`: member/file metadata is summarized without fetching payloads.
- `D4_content_indexed`: future extraction-policy depth, not approved here.
- `D5_action_indexed`: future action-policy depth, never default permission.

H0-BUNDLE-03 examples stop at local dry-run/fixture/audit posture. Coverage
records preserve review gates and blocked operations so later H1 tasks can add
policy packs deliberately.
