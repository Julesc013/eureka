# Token And Auth Gate Status

Token-free v0 is the default posture. No credentials are configured, tokens are
disabled, and private/credentialed access remains forbidden. In short: tokens are disabled.

Connector-specific status:

- Internet Archive metadata: token/auth disabled for v0 unless future policy changes.
- Wayback/CDX/Memento: token/auth disabled for v0; arbitrary URL fetch remains forbidden.
- GitHub Releases: token/auth review required; token use disabled now; private or token-required repositories rejected.
- PyPI metadata: token/auth review required; token use disabled now; private or credentialed indexes rejected.
- npm metadata: token/auth review required; token use disabled now; private scopes and credentialed registries rejected.
- Software Heritage: token/auth review required; token use disabled now; credentialed/private access rejected.

No token, API key, credential, account, or private source access was added.
