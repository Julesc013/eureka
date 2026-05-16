# GitHub Release Upload Plan

- mode: preview_only
- no_upload: true
- no_publish: true
- draft_ref: .aide/release/github-release-draft.json

## Asset Order
- 1: .aide/release/dist/aide-lite-pack-v0.zip (zip_archive) sha256=e5f714097effcce98d7263513d76a511fa8597aa468c0a4619af794240192553
- 2: .aide/release/dist/aide-lite-pack-v0.tar.gz (tar_gz_archive) sha256=594ae1d123c7962465efbf2ea49216fc80ec2d51149fee3dd0a20364ddebb8c6
- 3: .aide/release/dist/aide-lite-pack-v0.checksums.json (checksums) sha256=ab0498f724eb00eb2abe6fe74f571d0f5cddf2bfe004444f0200ebb1f0e72607
- 4: .aide/release/dist/SHA256SUMS.txt (sha256sums_text) sha256=f75d383a6ae762c700cd3d1bca0cd21f43354820ca3b224a4fbcfe05746bd91b
- 5: .aide/release/dist/manifest.yaml (manifest) sha256=c1e409ce684c736edc2c3f2586fced6f840180f9f9660f912b7ea8f32e58a18e
- 6: .aide/release/dist/install.md (install_notes) sha256=47bdd43779ea9c3c1cc1f35d8fea7a00f58ffb6cf17a362772b09b2e389d5bb8
- 7: .aide/release/dist/CHANGELOG.preview.md (changelog_preview_copy) sha256=4681c4a59a04225fc3345adce433b32f92dc1d9b23f5b3e28b57692faedf3136
- 8: .aide/release/dist/RELEASE_NOTES.preview.md (release_notes_preview_copy) sha256=db03847412e58581662c58f14f1ff3352d6966816352c3b9f779be8a75476ce6
- 9: .aide/release/dist/release-validation.json (validation_report) sha256=3f4164615521899ad86df1b9d57a122d9421cf777080d22d0ccc5b9aaaa7d5ad
- 10: .aide/release/dist/release-validation.md (validation_report) sha256=df35747cfd0d9361cf1dfd5d36a185bceb5e4939f0f892bb7dbb97da16040aae
- 11: .aide/release/dist/release-provenance.json (provenance_report) sha256=e85748d5067b50e157e3dbf800706fe9e485fc941e8dc8e7ee65f2b0ad1d93b3
- 12: .aide/release/dist/release-assets.json (asset_index) sha256=c27dd4c92195b8c3fcf64fa8049a8e88f1406b914c386c1a5969059417fa47e7

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
