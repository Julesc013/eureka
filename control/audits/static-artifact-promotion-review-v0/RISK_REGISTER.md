# Risk Register

| Risk | Status | Mitigation |
| --- | --- | --- |
| GitHub Pages run may fail despite local readiness | open | Run GitHub Pages Run Evidence Review v0 and record Actions evidence. |
| Static artifact can drift from sources | guarded | `static_site_dist` drift guard checks generator and artifact validators. |
| Historical stale-path references could be mistaken for current state | guarded | Repository layout validator and stale-reference review separate active references from historical audit evidence. |
| Public JSON could be overread as production API | guarded | Docs and validators retain static-summary and non-production language. |
| Future public search work could blur static/runtime boundary | open | Keep Public Search API Contract v0 separate and do not add runtime behavior here. |

No blocker prevents treating `site/dist/` as the active repo-local static
artifact. The remaining blocker is only for claiming live public deployment
success.
