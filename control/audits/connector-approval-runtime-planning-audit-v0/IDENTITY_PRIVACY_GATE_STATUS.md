# Identity And Privacy Gate Status

Identity and privacy gates remain policy-gated for every connector.

- Internet Archive metadata: item/source identifier review is required before live metadata use.
- Wayback/CDX/Memento: URI-R privacy review is required; arbitrary URL fetch is forbidden.
- GitHub Releases: owner/repo review is required; private repository and token-required repository access is rejected.
- PyPI metadata: package-name review is required; private/credentialed index access is rejected; dependency metadata remains cautionary.
- npm metadata: package-name and scoped-package review are required; private scopes are rejected; dependency metadata and lifecycle-script risks remain bounded.
- Software Heritage: SWHID, origin URL, and repository identity review are required; source-code-content fetch remains out of scope.

Public artifacts must not include private URLs, private repositories, private
package names, account IDs, tokens, emails, phone numbers, IP addresses, or user
identifiers.
