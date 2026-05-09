# Source Index Depth Model

Eureka uses D0-D5 to avoid false coverage claims.

- `D0_source_known`: source identity and policy posture are known.
- `D1_catalog_indexed`: catalog-level listing is represented.
- `D2_metadata_indexed`: metadata records are represented.
- `D3_representation_indexed`: representation/member metadata is represented.
- `D4_content_indexed`: content, OCR, text, manifests, or extracted members are represented.
- `D5_action_indexed`: safe action descriptors are represented.

A source can be known at D0/D1 without deeper indexing. D4 and D5 require
explicit extraction or action policies. D5 never implies download, install, or
execute permission by default.
