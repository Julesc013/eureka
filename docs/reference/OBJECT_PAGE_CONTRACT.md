# Object Page Contract v0

Object Page Contract v0 defines the future public page shape for resolved or provisional digital objects. It is contract-only: no runtime object pages, no object-page store, no hosted route, and no public search runtime behavior are implemented by P79.

Object pages are evidence-first. They answer what is known, what is provisional, what conflicts exist, which sources and evidence support a claim, what gaps remain, and what a user can safely do next. They are not an app store, not a downloader, not an installer, not an execution launcher, not a rights decision, not a malware-safety decision, and not candidate promotion.

## Object Identity, Status, And Lanes

The `object_identity` block separates `object_kind`, labels, aliases, identifiers, parent/child references, confidence, and `identity_status`. For v0, `identity_not_truth` is required because object page identity remains provisional unless a future governed authoritative model says otherwise.

The `object_status` block separates page lane (`official`, `preservation`, `community`, `candidate`, `absence`, `conflicted`, `demo`, `unknown`) from verification status (`fixture_backed`, `evidence_backed`, `candidate_only`, `review_required`, `insufficient_evidence`, `conflicted`, `synthetic_example`). Actionability is inspect-only, cite-only, compare-only, future-action-required, or no-safe-action.

## Versions, Representations, And Members

`versions_states_releases` records version/state labels, platform, architecture, source refs, evidence refs, confidence, and limitations. `representations` records metadata-only representations such as files, archives, installers, ISO records, packages, scans, web captures, source archives, and metadata records. `payload_included` and representation `downloads_enabled` must be false.

`members` models public-safe container members, such as a file inside an archive or a scan region. Member paths must be public-safe synthetic or reviewed values. No private paths and no raw payload dumps are allowed.

## Source, Evidence, And Provenance

`sources` records source family, status, source role, optional source-cache refs, and limitations. `evidence` records evidence kind/status, claim summary, provenance refs, confidence, and `confidence_not_truth`. Source cache and evidence ledger links are future references only; P79 performs no source cache mutation and no evidence ledger mutation.

## Compatibility

The compatibility block records supported, likely supported, unknown, likely unsupported, conflicting, or evidence-required states. It must not claim compatibility beyond evidence. Unknown compatibility is a first-class answer.

## Rights, Risk, And Actions

`rights_risk_action_posture` limits v0 object pages to safe actions: inspect metadata, view sources, view evidence, compare, and cite. Download, install, execute, upload, mirror, and arbitrary URL fetch are disabled. The contract makes no rights clearance and no malware safety claim.

## Conflicts, Duplicates, Absence, And Gaps

Conflicts are preserved instead of merged away. `destructive_merge_allowed` must be false. Absence is scoped only; `global_absence_claimed` must be false. Near misses and gaps explain source coverage gaps, capability gaps, compatibility evidence gaps, member access gaps, representation gaps, query interpretation gaps, live-probe-disabled gaps, external-baseline-pending gaps, deep extraction gaps, OCR gaps, source-cache gaps, and evidence-ledger gaps.

## Result-Card Projection

Object pages may project a public-safe summary into the public search result-card contract later. P79 only defines the result-card projection shape; it does not mutate public search, public index, local index, runtime index, or master index.

## API And Static Projection

Future route reservations are `/object/{object_id}` and `/api/v1/object/{object_id}`. `api_projection.implemented_now` must be false. Static projection is optional and contract-only in P79; no generated static object page was added.

## Privacy And Redaction

Public object page examples must contain no private absolute paths, no raw private queries, no private URLs, no account/user identifiers, no IP addresses, no credentials, and no raw payloads. Examples are synthetic and public-safe.

## Integration Boundaries

Object pages relate to public search through future result-card links, to public index through future generated summaries, to source cache and evidence ledger through future refs, to candidate index through provisional object identity, to candidate promotion policy through explicit review gates, and to known absence pages through scoped absence refs.

P79 adds no runtime object route, database, persistent object-page storage, source connector runtime, source cache runtime, evidence ledger runtime, candidate index runtime, no candidate promotion, live source call, external API call, telemetry, account system, download, install, execution, upload, arbitrary URL fetch, no public index mutation, local-index mutation, or no master index mutation.

## Future Work

The next page contract is Source Page Contract v0. Runtime object pages require separate approval, source/evidence runtime outputs, privacy review, action policy review, result-card integration review, and deployment evidence.
