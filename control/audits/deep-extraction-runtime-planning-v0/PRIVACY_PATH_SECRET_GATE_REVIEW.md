# Privacy Path Secret Gate Review

Current gate status:

- Private path rejection: documented.
- Path traversal rejection: documented.
- Home/user path rejection: documented.
- Private cache root rejection: documented.
- Secret/API key/token detection: documented.
- Private URL handling: private URLs rejected unless a future local-private
  policy is explicitly approved.
- IP/account/user identifier handling: public examples must not include them.
- Raw private query handling: forbidden.
- Public-safe output policy: logical container/member paths only.

Gaps:

- P105 does not add a runtime scanner.
- Future runtime must implement bounded error envelopes that never dump private
  payloads or private filenames.

