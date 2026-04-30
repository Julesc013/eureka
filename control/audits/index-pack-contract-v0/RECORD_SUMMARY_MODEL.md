# Record Summary Model

`record_summaries.jsonl` carries public-safe summaries. Each record includes:

- `record_id`
- `record_kind`
- `title`
- `source_id`
- `source_family`
- optional public target/reference fields
- optional representation/member/result-lane fields
- optional user-cost and compatibility summaries
- optional evidence count
- `public_safe`
- limitations

Allowed v0 record kinds are:

- `source_record`
- `resolved_object`
- `state_or_release`
- `representation`
- `member`
- `synthetic_member`
- `evidence`
- `article_segment`
- `other`

Record summaries do not include raw payloads, private paths, raw database row
ids, binary blobs, long copyrighted snippets, download URLs, install URLs, or
canonical truth claims.
