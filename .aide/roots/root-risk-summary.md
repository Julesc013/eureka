# Root Risk Summary

- no_apply: true
- deletion_approval: false

## Risks

- `.aide`: risk=high status=mixed reasons=identity_sensitive_hint, build_sensitive_file_hint, authority_sensitive_hint, generated_sensitive_content
- `.aide.local.example`: risk=high status=review_required reasons=unknown_kind_or_owner
- `.github`: risk=high status=review_required reasons=unknown_kind_or_owner
- `contracts`: risk=high status=review_required reasons=identity_sensitive_hint, authority_sensitive_hint, unknown_kind_or_owner
- `control`: risk=high status=mixed reasons=identity_sensitive_hint, build_sensitive_file_hint, unknown_kind_or_owner, multiple_file_kinds
- `crates`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `data`: risk=high status=review_required reasons=unknown_kind_or_owner
- `deploy`: risk=high status=review_required reasons=unknown_kind_or_owner
- `docs`: risk=low status=canonical reasons=unknown_kind_or_owner
- `evals`: risk=high status=review_required reasons=identity_sensitive_hint, unknown_kind_or_owner
- `examples`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `external`: risk=high status=review_required reasons=unknown_kind_or_owner
- `native`: risk=high status=mixed reasons=identity_sensitive_hint, build_sensitive_file_hint, authority_sensitive_hint, unknown_kind_or_owner
- `repo-root`: risk=high status=review_required reasons=authority_sensitive_hint, unknown_kind_or_owner
- `runtime`: risk=high status=mixed reasons=build_sensitive_file_hint, unknown_kind_or_owner, multiple_file_kinds
- `scripts`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `site`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `snapshots`: risk=high status=review_required reasons=identity_sensitive_hint, unknown_kind_or_owner
- `surfaces`: risk=high status=mixed reasons=build_sensitive_file_hint, unknown_kind_or_owner, multiple_file_kinds
- `tests`: risk=high status=review_required reasons=identity_sensitive_hint, build_sensitive_file_hint, unknown_kind_or_owner
