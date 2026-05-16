# Remaining Risks

- `origin/dev` is active and ahead of local `dev`; Q55 must stay local and must not push until the other machine pauses and a fresh sync is performed.
- Pre-existing untracked native build output remains outside Q54 scope: `native/win/winforms/src/Eureka/obj/`.
- Existing target AIDE has two broken report-only status commands: `gateway status` and `provider status` fail on missing source `core.*` modules.
- The stable source bundle is local preview/no-publish with `DIRTY_SOURCE_RECORDED`; Q55 must not call it an official release unless a later published release exists and is inspected.
- Broad secret scan is noisy because policy/test/source terms include `api_key`, `token`, and fixture forbidden-shape strings; Q55 should use both broad and strict scans and classify matches.
- Generated AIDE validation artifacts changed during Q54 and must be reviewed as generated evidence, not product truth.
- HUNT queue work is continuing remotely; the first post-upgrade product task must be chosen from the latest synchronized `origin/dev`, not this stale local queue alone.
