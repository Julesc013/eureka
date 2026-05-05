# URI Review And Normalization Plan

Allowed future URI sources:

- Reviewed source record.
- Reviewed search need.
- Source pack record.
- Manual observation record.
- Fixture example.

Forbidden URI sources:

- Raw public query parameter.
- Private URL.
- Credentialed URL.
- Localhost URL.
- File URL.
- Data URL.
- Javascript URL.
- Uploaded file.
- Local path.

Future normalization:

- Scheme and host normalization.
- Fragment stripping policy.
- Query-string redaction policy.
- Credential removal or rejection.
- Private host rejection.
- Public-safe hash/fingerprint for sensitive URI references.
- No raw private URL publication.

P88 implements none of this runtime behavior.
