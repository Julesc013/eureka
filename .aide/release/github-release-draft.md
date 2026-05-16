# AIDE Lite Pack v0 Draft (01f2470cc1c9346e)

> Local draft only. This release has not been published, tagged, uploaded, or sent to GitHub.

## Release Metadata

- Suggested tag: `aide-lite-pack-v0-draft-01f2470cc1c9346e`
- Suggested tag created: no
- Source commit: `01f2470cc1c9346ea2fecabe480555d8db9c1676`
- Source branch: `dev`
- Dirty state recorded: `true`
- Release type: local draft / not published

## Summary

- AIDE Lite Pack v0 local release bundle prepared for human review.
- Assets come from the Q47 local bundle under `.aide/release/dist/`.
- Install, repair, upgrade, rollback, and uninstall commands remain preservation-first planning surfaces.

## Release Notes Preview
- # AIDE Release Notes Preview
- This is a deterministic preview only. It does not publish a release.
- source_range: HEAD latest 50 commits
- source_head: df6a6967afdb510de46651f70e21541f20b6741b
- preview_only: true
- ## Highlights
- - Added: compatibility handling for historical candidate/probe/OBS references after schema moves. (5f5e5bcb22d2)
- - Added: source observation seam behavior and audit evidence for R0-04. (8bb9e4cd0bf5)

## Changelog Preview
- # AIDE Changelog Preview
- This file is generated from local Git history and is a preview only.
- source_range: HEAD latest 50 commits
- source_head: df6a6967afdb510de46651f70e21541f20b6741b
- commit_count: 50
- malformed_count: 0
- preview_only: true
- release_publishing: false

## Install Notes

- Local install notes: `.aide/release/dist/install.md`
- Default install workflow is observe, plan, dry-run, review.
- Target repositories must run their own validation after extraction/import.

## Assets

| Order | Asset | Kind | Size | SHA-256 | Required |
| --- | --- | --- | ---: | --- | --- |
| 1 | `.aide/release/dist/aide-lite-pack-v0.zip` | zip_archive | 717891 | `e5f714097effcce9...` | true |
| 2 | `.aide/release/dist/aide-lite-pack-v0.tar.gz` | tar_gz_archive | 468959 | `594ae1d123c79624...` | true |
| 3 | `.aide/release/dist/aide-lite-pack-v0.checksums.json` | checksums | 1200 | `ab0498f724eb00eb...` | true |
| 4 | `.aide/release/dist/SHA256SUMS.txt` | sha256sums_text | 690 | `f75d383a6ae762c7...` | true |
| 5 | `.aide/release/dist/manifest.yaml` | manifest | 1407 | `c1e409ce684c736e...` | true |
| 6 | `.aide/release/dist/install.md` | install_notes | 1251 | `47bdd43779ea9c3c...` | true |
| 7 | `.aide/release/dist/CHANGELOG.preview.md` | changelog_preview_copy | 20286 | `4681c4a59a04225f...` | true |
| 8 | `.aide/release/dist/RELEASE_NOTES.preview.md` | release_notes_preview_copy | 16033 | `db03847412e58581...` | true |
| 9 | `.aide/release/dist/release-validation.json` | validation_report | 3168 | `3f4164615521899a...` | false |
| 10 | `.aide/release/dist/release-validation.md` | validation_report | 239 | `df35747cfd0d9361...` | false |
| 11 | `.aide/release/dist/release-provenance.json` | provenance_report | 1441 | `e85748d5067b50e1...` | false |
| 12 | `.aide/release/dist/release-assets.json` | asset_index | 4961 | `c27dd4c92195b8c3...` | false |

## Validation Summary

- release validate: PASS
- pack-status: DIRTY_SOURCE_RECORDED
- fixture extraction: PASS
- checksum validation: PASS

## Known Risks
- This is a local draft only; no GitHub publication, tag, or upload has occurred.
- Suggested tag naming still requires human/operator review.
- Dominium and Eureka target install readiness are not claimed by Q48.
- Install, repair, upgrade, rollback, and uninstall remain plan/dry-run models unless a future phase adds apply behavior.
- Q47 bundle provenance records dirty source state; release reviewers must explicitly accept or regenerate from a clean state.

## Publication Blockers
- none for local draft generation

## Manual Publication Checklist

- Review this release body.
- Review suggested tag naming.
- Review asset list and checksums.
- Review known risks and target install caveats.
- Decide whether the eventual GitHub release is draft, pre-release, or stable.
- Obtain explicit operator approval before any future publication phase.

## Non-Publication Statement

- tag_created: no
- github_release_created: no
- upload_performed: no
- network_api_call: no
- branch_mutation: no
- active_ci_installed: no
