# GitHub Release Publication Checklist

- checklist_id: aide-lite-pack-v0-github-draft-6f2698c6e109a3b3-checklist
- source_commit: 6f2698c6e109a3b35d20402bb9871c1e4a674688
- no_publish: true

## Checks
- [source repo state] branch checked: recorded (dev)
- [source repo state] source commit recorded: recorded (6f2698c6e109a3b35d20402bb9871c1e4a674688)
- [source repo state] dirty state recorded: recorded (true)
- [source repo state] tag not created yet: pass (tag_created=false)
- [validation gates] release validate: required (.aide/release/dist/release-validation.md)
- [validation gates] draft validate: required (.aide/release/github-release-draft-validation.md)
- [artifact gates] zip exists: blocker (.aide/release/dist/aide-lite-pack-v0.zip)
- [artifact gates] tar.gz exists: blocker (.aide/release/dist/aide-lite-pack-v0.tar.gz)
- [artifact gates] checksums exist: blocker (.aide/release/dist/aide-lite-pack-v0.checksums.json)
- [artifact gates] manifest exists: blocker (.aide/release/dist/manifest.yaml)
- [artifact gates] install notes exist: blocker (.aide/release/dist/install.md)
- [security gates] no local state or secret assets: required (targeted secret scan)
- [target install caveats] target install readiness not claimed: pass (Q49/Q50/Q54/Q55 remain future work)

## Blockers
- missing required release asset: .aide/release/dist/aide-lite-pack-v0.zip
- missing required release asset: .aide/release/dist/aide-lite-pack-v0.tar.gz
- missing required release asset: .aide/release/dist/aide-lite-pack-v0.checksums.json
- missing required release asset: .aide/release/dist/SHA256SUMS.txt
- missing required release asset: .aide/release/dist/manifest.yaml
- missing required release asset: .aide/release/dist/install.md
- missing required release asset: .aide/release/dist/CHANGELOG.preview.md
- missing required release asset: .aide/release/dist/RELEASE_NOTES.preview.md
- Q47 release bundle validation failed; run release validate before publication review

## Warnings
- missing optional release asset: .aide/release/dist/release-provenance.json
- missing optional release asset: .aide/release/dist/release-assets.json

## Manual Review Required
- review release body
- review suggested tag
- review asset list
- review known risks
- review target install caveats
- decide whether this is pre-release/draft/stable
- decide whether to publish
