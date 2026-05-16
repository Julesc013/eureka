# Changelog Preview

Q27 adds deterministic changelog and release-note preview generation from
structured commit bodies.

```powershell
py -3 .aide/scripts/aide_lite.py changelog preview
py -3 .aide/scripts/aide_lite.py changelog preview --range HEAD~5..HEAD
```

Outputs:

- `.aide/changelog/CHANGELOG.preview.md`
- `.aide/changelog/RELEASE_NOTES.preview.md`
- `.aide/changelog/changelog.preview.json`
- `.aide/changelog/malformed-commits.md`

The preview groups `## Changelog` bullets by category and records malformed
commits instead of hiding them. It does not tag, publish, create releases,
mutate branches, call providers/models, or use the network.

Q31 exports the changelog preview command and reference docs to target repos,
but generated `.aide/changelog/*.preview.*` files remain source-specific
outputs and are not exported as target truth.
