# Audit Packs

`control/audits/` holds repo-governance audit packs. These packs are evidence
and planning artifacts, not product runtime behavior and not public product
claims.

An audit pack should usually be grouped under a dated directory and should include:

- a baseline record
- commands run or intended for final verification
- structure, content, behavior, and test-gap audits
- structured findings using `control/audits/schemas/finding.schema.json`
- backlog and next-milestone recommendations
- explicit non-goals and deferred items

Audit findings should map to future-work labels and should avoid vague
"improve everything" recommendations. If a finding depends on external search
quality, mark the external observation as pending manual evidence rather than
fabricating a baseline.

Audit packs must not be used to claim production readiness. Public-alpha
material remains supervised-demo evidence only until a separate accepted
hosting decision exists.

Current packs:

- `2026-04-25-comprehensive-test-eval-audit/`: repo-wide structure, content,
  behavior, test-gap, and backlog audit.
- `search-usefulness-delta-v0/`: stable usefulness-delta report comparing
  current Search Usefulness Audit output to a historical reported aggregate
  baseline after the old-platform/member-discovery implementation sequence.
- `search-usefulness-delta-v1/`: stable usefulness-delta report comparing
  post-source-expansion audit output to the v0 delta aggregate baseline and
  recording archive-eval movement toward source-backed but still unsatisfied
  hard tasks.
- `hard-eval-satisfaction-v0/`: stable archive-resolution hard-eval report
  recording the move from `capability_gap=1, not_satisfied=5` to
  `capability_gap=1, partial=5` without weakening hard tasks or fabricating
  source evidence.
- `old-platform-result-refinement-v0/`: stable archive-resolution result-shape
  report recording the move to `capability_gap=1, partial=4, satisfied=1`
  after deterministic primary-candidate, expected-lane, and bad-result checks
  were added without weakening hard tasks or changing retrieval behavior.
- `more-source-coverage-expansion-v1/`: stable targeted source-expansion
  report recording the move to `capability_gap=1, satisfied=5` for current
  archive-resolution hard evals after tiny Firefox XP, blue FTP-client XP,
  Windows 98 registry repair, and Windows 7 utility/app fixture evidence was
  added without live source behavior, real binaries, or external baseline
  claims.
- `article-scan-fixture-pack-v0/`: stable article/scan fixture report
  recording the move to `satisfied=6` for current archive-resolution hard evals
  after a tiny synthetic article segment, page-range locator, and OCR-like text
  fixture were added without live source behavior, OCR engines, PDF/image
  parsing, real magazine scans, copyrighted article text, or external baseline
  claims.

- `post-queue-state-checkpoint-v0/`: post-queue repo-state checkpoint after the
  publication/static/live-alpha/Rust/snapshot queue. It records milestone
  evidence, command results, eval/audit status, external-baseline pending
  status, risks, deferrals, and next planning without adding product behavior.
- `native-client-project-readiness-v0/`: conservative readiness review for
  future native client project scaffolding. It records contract coverage, lane
  readiness, risks, a pre-native checklist, and a human-approval gate without
  adding Visual Studio/Xcode projects, native app code, GUI behavior, FFI,
  downloads, installers, cache runtime, relay runtime, or live probes.
- `windows-7-winforms-native-skeleton-planning-v0/`: planning pack for the
  first future Windows 7 SP1+ x64 WinForms .NET Framework 4.8 skeleton. It
  records proposed path, namespace, build-host requirements, allowed/prohibited
  initial scope, data inputs, and approval gates without creating `clients/`,
  Visual Studio project files, C# source, GUI behavior, FFI, downloads,
  installers, cache runtime, relay runtime, or live probes.
- `relay-prototype-planning-v0/`: planning pack for the first future relay
  prototype. It selects a localhost-only/read-only/static
  `local_static_http_relay_prototype`, records input/output contracts,
  security/privacy defaults, operator gates, risks, and implementation
  boundaries without creating a relay server, opening sockets, adding protocol
  support, serving private files, proxying a live backend, enabling live probes,
  or claiming old-client relay support.
- `full-project-state-audit-v0/`: full project checkpoint after the
  backend/source/eval/publication/snapshot/relay/native-policy/native-planning
  and Rust parity planning sequence. It records milestone status, verification
  results, eval/search status, external-baseline pending state,
  publication/static/public-alpha posture, source/retrieval state,
  snapshot/relay/native/Rust status, risks, blockers, human-operated work,
  explicit deferrals, and next milestone recommendations without changing
  product behavior.
- `public-data-contract-stability-review-v0/`: field-level public data
  stability review for generated static JSON under `site/dist/data/`. It
  classifies files and fields as `stable_draft`, `experimental`, `volatile`,
  `internal`, `deprecated`, or `future`, records versioning/breaking-change
  policy, and recommends Generated Artifact Drift Guard v0 without changing
  product behavior or claiming production API stability.
- `generated-artifact-drift-guard-v0/`: validation/audit pack for generated and
  generated-like artifact ownership. It covers public data, compatibility
  surfaces, static demos, seed snapshots, `site/dist`, Python oracle goldens,
  public-alpha rehearsal evidence, publication inventories, test registry
  metadata, and AIDE metadata without regenerating artifacts by default,
  changing product behavior, deploying, or calling external services.
- `static-artifact-promotion-review-v0/`: local promotion review for the
  generated `site/dist` artifact. It conditionally promotes `site/dist` as the
  active repo-local static artifact, records workflow/generated-artifact/safety
  and stale-reference evidence, and leaves GitHub Actions deployment evidence
  unverified without adding runtime behavior or production claims.
