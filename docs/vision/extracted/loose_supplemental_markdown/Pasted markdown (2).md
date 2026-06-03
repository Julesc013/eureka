GPT-5.5 Pro — 2026-06-03 18:28:20 Australia/Melbourne

## Verdict

Yes, this is close to the best architecture, but the framing should be upgraded one more level.

The thing you want is not just a **temporal design system**. It is a:

> **Temporal Semantic Interface System**

That means:

```text
Eureka has one semantic product language.
That language has versioned contracts.
Those contracts generate every page, API response, terminal screen, native view, file manifest, snapshot, and future AI/agent response.
```

The invariant should be:

```text
One object model.
One route model.
One evidence model.
One action model.
One resolution/run model.
One capability model.
Many representations.
Many skins.
Many clients.
No duplicated product logic.
```

This matches the current architecture direction: the retrieved plan says not to hardwire a browser page to a specific Internet Archive bridge, but to route search through a `ResolutionRunKernel`, commands/events, work units, lane projection, and projection adapters; it also states the core modular boundary as “kernel owns behavior, surfaces own rendering, contracts own meaning, policies own permissions, stores own persistence.” 

The missing layer is the **Surface/Representation Kernel** that sits beside the `ResolutionRunKernel`.

---

# 1. What you are still missing

## 1.1 A formal semantic interface contract

You have named the right primitives:

```text
Search
Object
Need
Candidate
Source
Pack
Task
Evidence
Action
Status
Review
Compare
Account
```

But they need to become **versioned interface contracts**, not just conceptual page types.

Add:

```text
contracts/semantic/
  eureka_entity.v0.json
  eureka_action.v0.json
  eureka_status.v0.json
  eureka_badge.v0.json
  eureka_navigation.v0.json
  eureka_affordance.v0.json

contracts/views/
  search_page.v0.json
  result_card.v0.json
  object_page.v0.json
  need_page.v0.json
  candidate_page.v0.json
  source_page.v0.json
  pack_page.v0.json
  task_page.v0.json
  evidence_page.v0.json
  review_page.v0.json
  compare_page.v0.json
  account_page.v0.json
  status_page.v0.json
```

The page is not the source of truth. The **view model** is.

---

## 1.2 A Surface Kernel

You already need a `ResolutionRunKernel` for search/run behavior. The retrieved plan identifies that missing kernel and says it should own run creation, query compilation handoff, state machine, event log, control commands, policy gates, work-unit scheduling, lane assembly, coverage reports, blocked-action posture, and projection-safe output. 

Now add:

```text
SurfaceKernel
  route resolution
  canonical view-model loading
  capability negotiation
  representation selection
  renderer dispatch
  skin selection
  cache key generation
  output policy enforcement
  fallback generation
```

Relationship:

```text
Request
→ RouteKernel
→ ResolutionRunKernel / ObjectStore / EvidenceStore
→ Canonical View Model
→ SurfaceKernel
→ Representation
→ Client
```

This prevents the UI layer from becoming another source of fragmentation.

---

## 1.3 Representation contracts

Each representation profile needs a machine-readable contract.

```text
contracts/representations/
  representation_profile.v0.json
  capability_manifest.v0.json
  renderer_contract.v0.json
  skin_contract.v0.json
  compatibility_budget.v0.json
  fallback_rule.v0.json
```

Example:

```json
{
  "profile_id": "html32",
  "media_type": "text/html",
  "requires": {
    "html": "3.2",
    "css": "none",
    "javascript": false,
    "tables": true,
    "forms": true,
    "unicode": "limited"
  },
  "forbids": [
    "client_side_routing",
    "fetch_api",
    "web_components",
    "canvas_required",
    "svg_required"
  ],
  "max_page_weight_kb": 64,
  "fallback_chain": ["html2", "text", "manifest"]
}
```

Without this, “classic,” “lite,” and “terminal” become vibes instead of testable targets.

---

## 1.4 A compatibility lab

You need a test harness that proves the same entity works across decades.

Add:

```text
tests/compatibility/
  render_search_html2_test.py
  render_search_html32_test.py
  render_search_text_test.py
  render_object_terminal_test.py
  render_object_modern_test.py
  render_need_snapshot_test.py
  no_js_search_test.py
  low_bandwidth_budget_test.py
  no_css_readability_test.py
  ascii_fallback_test.py
  old_url_contract_test.py
```

Acceptance should include:

```text
/search renders in text, html2, html32, classic, rich, json.
/object/{id} renders in text, html2, html32, classic, rich, json.
/need/{id} renders in text, html2, html32, classic, rich, json.
No renderer is allowed to invent facts.
No renderer is allowed to hide candidate/verified status.
No renderer is allowed to expose forbidden actions.
```

This is what makes compatibility real instead of aspirational.

---

# 2. The best final architecture

## 2.1 Core stack

```text
Eureka Domain Core
  object model
  evidence model
  source model
  need model
  candidate model
  pack model
  task model
  review model
  action model

ResolutionRunKernel
  query/run behavior
  work units
  events
  lanes
  policy gates
  review bridge

SurfaceKernel
  canonical view models
  capability negotiation
  representation selection
  renderer dispatch

Renderer Registry
  api_json
  xml
  rss
  atom
  text
  markdown
  terminal
  html2
  html32
  html4_classic
  classic_search
  lite
  rich
  native_card
  agent_context
  snapshot

Skin Registry
  eureka_default
  classic_search_1998
  classic_search_2004
  classic_search_2010
  terminal
  print
  high_contrast

Policy Engine
  source policy
  rights policy
  risk policy
  action policy
  auth policy
  legacy-surface policy

Cache/Index Layer
  master index
  candidate index
  query intelligence index
  source cache
  rendered-view cache
  static snapshot cache
```

The existing plan already says source expansion should wait until a reusable orchestration layer exists, because otherwise you multiply per-source scripts; it recommends “one run kernel, one WorkUnit scheduler, one lane projector, one review bridge, many source adapters.” 

Extend that principle:

```text
one surface kernel
one capability negotiator
one renderer registry
many representations
```

---

# 3. The missing doctrine: semantic affordances

A normal design system says:

```text
Button
Card
Table
Modal
Nav
```

Eureka should instead define **affordances**:

```text
Open
Inspect
Compare
Watch
Export
Cite
DownloadManifest
RunTask
SubmitEvidence
ReviewCandidate
Promote
Reject
ReportRisk
Preserve
Replay
InstallHandoff
```

Then each renderer decides how to express them.

Example:

| Affordance         | Modern web       | HTML 3.2 | Text            | Terminal       | Native                |
| ------------------ | ---------------- | -------- | --------------- | -------------- | --------------------- |
| `Compare`          | button/panel     | link     | numbered action | command        | native split view     |
| `Evidence`         | expandable graph | table    | evidence list   | command view   | native evidence sheet |
| `WatchNeed`        | account button   | link     | “watch URL”     | `WATCH 4`      | notification toggle   |
| `DownloadManifest` | action card      | link     | manifest path   | `GET MANIFEST` | download queue item   |

This preserves feature parity without pretending every client can render the same widget.

---

# 4. The “same code” correction

You cannot literally use the same UI code on a 1970s terminal, a 1990s browser, a 2020s web app, iOS, Android, and an AI agent.

The correct target is:

```text
same contracts
same route semantics
same view models
same action model
same policy decisions
same evidence
different renderers
different transport adapters
```

That is stronger than “same code,” because it is testable and portable.

Use generated client/render bindings where possible:

```text
contracts/
  ↓ generate
Python server models
TypeScript web models
Rust/CLI models
Swift/Kotlin native models
JSON Schema validators
fixture render tests
```

---

# 5. Representation matrix: final form

## 5.1 Machine representations

```text
application/json
application/xml
application/atom+xml
application/rss+xml
application/vnd.eureka.object+json
application/vnd.eureka.search+json
application/vnd.eureka.manifest+json
```

Use these for APIs, agents, native clients, packs, snapshots, and integrations.

## 5.2 Human text representations

```text
text/plain
text/markdown
text/vnd.eureka.terminal
```

Use these for terminals, old clients, text browsers, serial relays, snapshots, and debugging.

## 5.3 Web representations

```text
html2
html32
html4-classic
classic-search
lite
rich
print
```

The baseline search form should remain a plain HTML form. The HTML standard defines the `form` element as a hyperlink-like element with form-associated controls that submit editable values to a server, and the spec includes search-form examples using `method="get"` and an input named `q`. ([html.spec.whatwg.org][1])

## 5.4 Native representations

```text
native_card
native_list
native_object_page
native_action_sheet
native_manifest
```

These are view-model projections, not independent product logic.

## 5.5 Future representations

```text
agent_context
voice_summary
AR_card
model_context_pack
autonomous_task_bundle
```

Same semantic entities. New renderers.

---

# 6. Capability negotiation: final form

HTTP already supports content negotiation because a server can choose between different representations based on user-agent preferences, capabilities, languages, formats, or encodings; RFC 9110 defines proactive, reactive, and request-content negotiation patterns. ([rfc-editor.org][2]) The `Accept` header lets user agents specify preferred response media types, and `Vary` tells caches which request fields influenced representation selection. ([rfc-editor.org][2]) ([rfc-editor.org][2])

Use this order:

```text
1. Explicit route parameter
   ?format=text
   ?profile=classic
   ?skin=classic-search-2004

2. Account/device preference
   user says "always use classic"

3. Native/relay capability manifest
   app declares what it supports

4. Host profile
   old.example.org forces legacy-safe default

5. HTTP Accept / Accept-Language / Accept-Encoding

6. Client hints where available

7. User-agent fallback

8. safest default:
   server-rendered no-JS HTML
```

Do **not** let negotiation change identity. It only changes representation.

```text
/object/eu_123
```

is the same object in JSON, terminal, HTML 3.2, classic search, and rich web.

---

# 7. Performance model

## 7.1 Precompute canonical view models

Do not render every page from raw database joins every time.

Use:

```text
object/eu_123
  → ObjectPageView v0
  → render html32
  → render classic
  → render rich
  → render text
  → render json
```

Cache layers:

```text
L1 request cache
L2 rendered representation cache
L3 canonical view-model cache
L4 index/object/evidence store
L5 source cache
```

## 7.2 Use representation budgets

Define hard budgets:

| Profile   |                                    Target |
| --------- | ----------------------------------------: |
| `text`    |                        < 16 KB first page |
| `html2`   |                                   < 32 KB |
| `html32`  |                                   < 64 KB |
| `classic` |                                  < 128 KB |
| `lite`    |                                  < 200 KB |
| `rich`    | < 500 KB initial HTML, progressive assets |
| `native`  |              paginated JSON/card payloads |

No renderer should be allowed to accidentally send a 2 MB object page to a 1998 browser.

## 7.3 Cache correctly

Because negotiated responses vary by profile/media type, cache keys must include:

```text
route
entity_id
view_model_version
renderer_id
profile_id
skin_id
language
auth/public state
policy posture
```

And HTTP responses should emit appropriate `Vary` headers when headers influence representation selection. The `Vary` header exists specifically to describe what parts of the request influenced response selection. ([rfc-editor.org][2])

---

# 8. Reliability model

Add three invariants.

## 8.1 Renderers are pure

A renderer must be:

```text
view_model + profile + skin + policy_context
→ representation
```

It must not:

```text
query sources
mutate records
promote candidates
infer facts
change policy
```

## 8.2 Unknown fields must not break clients

All contracts need forward-compatible rules:

```text
unknown fields ignored
unknown actions hidden or shown as unsupported
unknown badges rendered as text
unknown status shown as "unknown"
unknown evidence type linked, not interpreted
```

This is essential for old clients and future clients.

## 8.3 Every representation must expose state

No matter how limited the client is, it must still show:

```text
verified / candidate / need / near miss / policy-blocked
source
evidence summary
risk
rights
compatibility
available actions
```

A text-only client may be simple, but it must not be misleading.

---

# 9. Moddability and extension

The extension model should be more general than source connectors.

## 9.1 Plugin types

```text
source connector
extractor
renderer
skin
ranking feature
policy pack
pack validator
action backend
native bridge
agent provider
translation/transliteration provider
compatibility database provider
```

## 9.2 Plugin manifest

```json
{
  "plugin_id": "eureka.renderer.html32",
  "kind": "renderer",
  "version": "0.1.0",
  "input_contracts": ["object_page.v0", "search_page.v0"],
  "output_profiles": ["html32"],
  "permissions": [],
  "side_effects": false,
  "deterministic": true,
  "max_output_kb": 64,
  "test_fixtures_required": true
}
```

## 9.3 Isolation rule

Untrusted plugins should run out-of-process or in a sandbox. Renderers should not receive secrets. Connectors should not receive account tokens unless explicitly authorized. Action backends should pass through policy gates.

---

# 10. Compatibility you have not fully covered

## 10.1 Character encoding fallback

Canonical data should be Unicode. Representations may need fallback.

```text
canonical: UTF-8
html4/classic: UTF-8 if supported, otherwise declared fallback
text/ascii: transliteration + loss markers
terminal: UTF-8, CP437, MacRoman, ISO-8859-1 variants where needed
```

If a title cannot be rendered faithfully:

```text
München
→ Munchen [lossy]
```

Never silently corrupt meaning.

## 10.2 Date/time rendering

Canonical dates should be structured:

```json
{
  "date_kind": "publication_date",
  "value": "1998-05-12",
  "precision": "day",
  "calendar": "gregorian",
  "source": "..."
}
```

Old renderers can show plain text. Rich renderers can show uncertainty. Same data.

## 10.3 Link and action degradation

Some clients can open a WARC replay. Some can only download a manifest. Some can only display a citation.

So every action needs:

```text
requires
forbids
fallback_action
unsafe_reason
policy_reason
```

Example:

```text
Replay capture
  fallback: show capture metadata + manifest
```

## 10.4 Authentication compatibility

Do not force modern auth onto old clients.

Use:

```text
anonymous read-only search
device code login
relay-authenticated old client
short-lived scoped tokens
manifest-only public access
```

Never expose account cookies or write actions over unsafe legacy HTTP.

## 10.5 Offline-first snapshots

Every major public surface should be snapshot-able:

```text
/search snapshots for curated queries
/object snapshots
/source snapshots
/need snapshots
/index bundle
/manifest bundle
/text bundle
/ftp mirror bundle
```

This is how CD-ROM, LAN, BBS, FTP, offline nodes, and future preservation mirrors all consume the same system.

---

# 11. UX improvements still missing

## 11.1 State language

Use one status vocabulary everywhere:

```text
Verified
Candidate
Need
Near miss
Mention only
Policy-blocked
Private local
Superseded
Rejected
Unknown
```

Do not use synonyms like “maybe,” “draft,” “unconfirmed,” “provisional,” and “candidate” interchangeably. Pick one canonical state table.

## 11.2 Result reason grammar

Every result should have a short reason string:

```text
Ranked because title, version, platform, and source matched.
Demoted because hash is missing.
Shown as candidate because evidence is not yet reviewed.
Shown as near miss because version differs.
```

Same reason appears in modern card, terminal, text, API, and native app.

## 11.3 Universal action row

Every entity page should expose a consistent action grammar:

```text
View
Evidence
Compare
Manifest
Watch
Discuss
Contribute
Report
Export
```

Order should not randomly change by renderer.

## 11.4 “What changed?” affordance

For returning users and nodes:

```text
changed since last visit
new candidates
new evidence
candidate promoted
candidate rejected
source refreshed
risk changed
rights changed
```

This is essential for a self-improving system.

---

# 12. Accessibility as a structural feature

Accessibility should not be bolted onto the rich web version. It should be enforced at the semantic/view-model level:

```text
every action has a label
every status has text, not color only
every evidence badge has machine-readable meaning
every relationship can render as text
every graph has an edge-list fallback
every filter has a form fallback
```

WCAG 2.2’s top-level accessibility principles are perceivable, operable, understandable, and robust; those map directly to Eureka’s goal of surviving across clients and capabilities. ([W3C][3])

---

# 13. Security and privacy gaps

The temporal system creates unusual risks.

## 13.1 Legacy host isolation

If you support:

```text
http://old.example.org
```

then it must be:

```text
public
read-only
no account cookies
no secrets
no write actions
no user-specific private results
no privileged API calls
```

## 13.2 Renderer policy

A renderer cannot decide whether to show a download/install action. The policy engine decides. The renderer only displays allowed actions.

## 13.3 Query privacy

Text/terminal/old-browser logs can be sensitive. Query intelligence should store normalized, privacy-filtered observations, not raw sensitive data.

## 13.4 Public contribution defense

If the system becomes moddable and contributory:

```text
pack validation
signature checks
quarantine
review queues
rate limits
risk labels
reputation
takedown workflow
abuse reports
```

become part of the product, not back-office plumbing.

---

# 14. The ultimate repository structure

```text
/
  README.md
  LICENSE
  SECURITY.md

  docs/
    architecture/
      TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md
      SURFACE_KERNEL.md
      RESOLUTION_RUN_KERNEL.md
      CAPABILITY_NEGOTIATION.md
      RENDERER_POLICY.md
    product/
      PUBLIC_SEARCH_UX.md
      OBJECT_PAGE_UX.md
      NEED_PAGE_UX.md
      CANDIDATE_PAGE_UX.md
      SOURCE_PAGE_UX.md
      CONTRIBUTION_UX.md
    operations/
      HOSTING.md
      SNAPSHOTS.md
      LEGACY_HTTP_POLICY.md
      CACHE_POLICY.md
      ROLLBACK.md

  contracts/
    semantic/
    entities/
    views/
    resolution_run/
    representations/
    packs/
    api/
    actions/
    policy/

  runtime/
    domain/
    resolution_run/
    surface/
      surface_kernel.py
      route_resolver.py
      capability_negotiator.py
      view_model_loader.py
      renderer_dispatch.py
      cache_key.py
    source_observation/
    policy/
    packs/
    query_intelligence/
    review/

  renderers/
    api_json/
    xml/
    rss/
    atom/
    text/
    markdown/
    terminal/
    html2/
    html32/
    html4_classic/
    classic_search/
    lite/
    rich/
    native_card/
    agent_context/

  skins/
    eureka_default/
    classic_search_1998/
    classic_search_2004/
    classic_search_2010/
    terminal/
    high_contrast/
    print/

  services/
    web/
    api/
    worker/
    indexer/
    snapshot/
    relay/

  apps/
    cli/
    tui/
    desktop/
    mobile/
    relay/

  data/
    fixtures/
    seeds/
    golden_views/
    compatibility_corpus/

  tests/
    contract/
    renderer/
    compatibility/
    accessibility/
    performance/
    policy/
    e2e/

  infra/
    docker/
    caddy/
    nginx/
    cloudflare/
    systemd/
    backup/

  scripts/
    build_views.py
    render_fixture.py
    validate_contracts.py
    validate_renderers.py
    build_snapshot.py
    run_resolution.py
```

---

# 15. The implementation sequence

## TSIS-00 — Doctrine and contracts

```text
TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md
semantic primitive table
canonical status vocabulary
canonical action vocabulary
canonical page/view model list
```

## TSIS-01 — Surface Kernel

```text
runtime/surface/
  surface_kernel.py
  route_resolver.py
  capability_negotiator.py
  renderer_dispatch.py
```

## TSIS-02 — Canonical view models

```text
SearchPageView
ResultCardView
ObjectPageView
NeedPageView
CandidatePageView
SourcePageView
PackPageView
TaskPageView
EvidencePageView
StatusPageView
```

## TSIS-03 — Baseline renderers

Build in this order:

```text
json
text
html2
classic_search
rich
```

Reason: JSON proves contract correctness, text proves semantic fallback, HTML2 proves durability, classic proves default UX, rich proves modern enhancement.

## TSIS-04 — Renderer golden tests

For each fixture:

```text
same object
same status
same actions
same evidence
rendered to all profiles
```

## TSIS-05 — Capability negotiation

Support:

```text
Accept
format/profile query params
host profile
device profile manifest
account preference
fallback chain
```

## TSIS-06 — Public UX rebuild

```text
home
search results
object page
need page
candidate page
source page
pack page
status page
```

## TSIS-07 — Snapshot and relay

```text
static snapshots
text bundles
FTP/file manifests
local relay mode
terminal profile
```

## TSIS-08 — Modding SDK

```text
renderer plugin manifest
skin manifest
policy pack
contract validator
golden fixture requirement
```

## TSIS-09 — Performance and accessibility gates

```text
page weight budgets
no-JS gates
keyboard gates
text fallback gates
WCAG-oriented checks
old-client render checks
```

---

# 16. What is “best” here?

The best architecture is not the one with the most renderers. It is the one where adding a new renderer does not change the product.

The test:

```text
Can we add a VT100 renderer without changing search logic?
Can we add an iOS renderer without changing evidence logic?
Can we add a 2004 classic skin without changing route logic?
Can we add an AI-agent context response without changing object identity?
Can we add a new source without changing result page semantics?
Can we add a new action without every renderer breaking?
```

If yes, the architecture is right.

---

# 17. Final answer

The current idea is the strongest direction, but the ultimate version is:

> **Temporal Semantic Interface System + ResolutionRunKernel + SurfaceKernel + Renderer Registry + Capability Negotiator + Policy Engine + Contract-Governed View Models.**

What you were missing is mainly:

```text
formal semantic contracts
SurfaceKernel
renderer/plugin contracts
capability test matrix
performance budgets per representation
semantic affordance model
unknown-field forward compatibility
legacy auth/security boundaries
snapshot/relay packaging
accessibility as a structural primitive
modding contracts
golden cross-render tests
```

The final doctrine:

```text
Eureka does not have pages.
Eureka has semantic entities.

Eureka does not have UI tiers.
Eureka has negotiated representations.

Eureka does not clone old interfaces.
Eureka renders the same archive language through the idioms each machine understands.

Eureka does not duplicate logic per client.
Eureka centralizes meaning, policy, evidence, actions, and runs; clients only project them.
```

That is the most robust path: powerful enough for future AI/native clients, simple enough for text and old browsers, and disciplined enough to avoid turning into a pile of separate products.

[1]: https://html.spec.whatwg.org/multipage/forms.html "HTML Standard"
[2]: https://www.rfc-editor.org/rfc/rfc9110.html "RFC 9110: HTTP Semantics"
[3]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"
