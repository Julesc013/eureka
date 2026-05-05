# Security And Abuse Review

Risks that keep runtime gated:

- archive bombs
- path traversal / zip-slip
- symlinks and hardlinks
- nested archives
- malicious installers
- lifecycle scripts
- macros
- executable payloads
- huge text/OCR inputs
- private file leakage
- URL smuggling
- public-search extraction-on-demand abuse
- connector-triggered extraction abuse
- pack-import extraction abuse
- retry storms
- sandbox escape risk

Required controls:

- operator kill switch
- network disabled
- execution disabled
- sandbox required
- resource limits approved
- no public request parameter may select paths, URLs, stores, queues, indexes, or
  source roots

