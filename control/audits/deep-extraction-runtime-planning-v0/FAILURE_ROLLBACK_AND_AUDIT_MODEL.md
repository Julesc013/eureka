# Failure Rollback And Audit Model

Future failure classes:

- invalid request
- unsupported container
- sandbox unavailable
- resource limit exceeded
- decompression bomb suspected
- path traversal detected
- executable payload detected
- private path or secret detected
- OCR/transcription disabled
- manifest parse failure
- cleanup failure

Rollback model:

- no partial mutation because mutation is forbidden
- temporary workspace cleanup required
- bounded error envelope required
- audit report must not include private payload dumps, private filenames, raw
  copyrighted payloads, or secrets

