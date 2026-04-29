# Risks

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Stable-draft overread | File-level `stable_draft` could make clients depend on every nested field. | This review scopes stability to listed field paths only. |
| Generated artifact drift | Public data, `site/dist`, snapshots, demo data, and file-tree surfaces can drift independently. | Run Generated Artifact Drift Guard v0 next. |
| Volatile counts treated as benchmarks | Eval/search counts can move as fixtures or audit taxonomy change. | Mark audit detail counts experimental or volatile. |
| Internal path leakage as API | `source_inputs` and `source_file` are useful diagnostics but should not be client contracts. | Mark internal and validate clients do not need them. |
| Capability overclaiming | Source capability booleans are tempting compatibility promises. | Mark capability details experimental. |
| Snapshot/native/relay premature dependence | Future consumers may treat public JSON as production API. | Require version checks and policy references. |
| Deployment overclaim | Static data can be mistaken for hosted deployment proof. | Keep no-deployment and no-live flags stable-draft and false. |
| External-baseline fabrication | Eval summary can be misread as observed external comparison. | Keep observed counts explicit and no external observations false. |
