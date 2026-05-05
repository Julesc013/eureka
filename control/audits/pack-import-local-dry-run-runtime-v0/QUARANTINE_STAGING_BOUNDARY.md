# Quarantine And Staging Boundary

P104 does not create a real quarantine or staging store. It may report how a
pack would be classified for future staging, but it does not copy arbitrary
packs, write staging manifests, write quarantine state, or stage real packs.

The staged-pack inspector remains separate and may be run only against approved
repo examples when safe. Real quarantine/staging runtime remains future and
operator-approved.
