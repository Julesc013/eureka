# Rollback Plan

Rollback must cover:

- bad deploy
- bad renderer
- bad index build
- bad reviewed record promotion
- bad candidate batch
- bad source-family behavior
- fallback runaway

Controls:

- disable fallback
- disable source family
- freeze review promotion
- revert public index/snapshot to prior manifest
- roll back deployment

