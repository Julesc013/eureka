# Search Field Model

Public documents expose:

- identity fields: `doc_id`, `record_id`, `record_kind`, `public_target_ref`
- presentation fields: `title`, `subtitle`, `description`
- source fields: `source_id`, `source_family`, `source_status`, coverage depth
- matching fields: platform, architecture, version, date, keyword terms
- evidence and compatibility summaries
- action posture: allowed safe actions and blocked unsafe actions
- warnings and limitations
- `search_text` for deterministic lexical matching

The field model intentionally avoids private paths, credentials, raw payloads,
binary data, and request-selectable index metadata.
