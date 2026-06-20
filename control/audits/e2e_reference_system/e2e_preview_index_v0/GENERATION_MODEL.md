# Generation Model

Each build writes an immutable generation under:

```text
.eureka/e2e-reference/preview-index/generations/<preview-index-id>/
```

Generation IDs are deterministic content IDs derived from sorted preview records
and input source manifest hashes. The root `current.json` pointer identifies the
active generation. Rebuilding the same inputs yields the same generation ID and
record bytes.
