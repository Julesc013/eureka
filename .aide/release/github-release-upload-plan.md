# GitHub Release Upload Plan

- mode: preview_only
- no_upload: true
- no_publish: true
- draft_ref: .aide/release/github-release-draft.json

## Asset Order
- 1: .aide/release/dist/aide-lite-pack-v0.zip (zip_archive) sha256=
- 2: .aide/release/dist/aide-lite-pack-v0.tar.gz (tar_gz_archive) sha256=
- 3: .aide/release/dist/aide-lite-pack-v0.checksums.json (checksums) sha256=
- 4: .aide/release/dist/SHA256SUMS.txt (sha256sums_text) sha256=
- 5: .aide/release/dist/manifest.yaml (manifest) sha256=
- 6: .aide/release/dist/install.md (install_notes) sha256=
- 7: .aide/release/dist/CHANGELOG.preview.md (changelog_preview_copy) sha256=
- 8: .aide/release/dist/RELEASE_NOTES.preview.md (release_notes_preview_copy) sha256=
- 9: .aide/release/dist/release-validation.json (validation_report) sha256=7d49badf0c8e63fda54a514eab1ce1aeaa6f82d0a6b219cd56c9e80ce3d48a0d
- 10: .aide/release/dist/release-validation.md (validation_report) sha256=727a6453692de5f232ad4a1e16b6fd5b4dbada88db899468252f132308d19864
- 11: .aide/release/dist/release-provenance.json (provenance_report) sha256=
- 12: .aide/release/dist/release-assets.json (asset_index) sha256=

## Blocked Actions
- create_git_tag
- push_git_tag
- create_github_release
- upload_release_asset
- publish_package
- mutate_branch
- mutate_github_settings
- install_ci
- call_network
- call_provider_model

## Prerequisites
- release bundle validation pass
- pack-status pass
- draft validation pass
- secret scan pass
- asset list reviewed
- publication checklist reviewed
- explicit operator approval
- tag naming decision
