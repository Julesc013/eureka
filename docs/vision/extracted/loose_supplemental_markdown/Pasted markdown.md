GPT-5.5 Pro — 2026-06-03 20:25:41 AEST

## Verdict

Yes: **Temporal Semantic Interface System** is the right next architectural doctrine.

But the best directory structure is **not** the large generic one with new top-level roots like:

```text
renderers/
skins/
services/
apps/
data/
infra/
```

The better long-lived structure is:

```text
closed root model
semantic contracts
runtime kernels
surface projections
governed examples/snapshots/site outputs
tests that prove every representation says the same thing
```

So the answer is:

```text
Keep Eureka’s current root structure.
Add TSIS inside the existing roots.
Do not create new top-level product categories.
```

Your recent repo state already points this way: current repo health says the next task is source/snapshot baseline closeout via external full-discovery handoff, not another directory refactor; it also records source action, source wave, and snapshot relay as completed with warnings requiring external discovery evidence. 

---

# 1. Best final top-level structure

Keep this:

```text
eureka/
  .aide/
  .aide.local.example/
  .github/

  control/
  contracts/
  runtime/
  surfaces/
  site/
  snapshots/
  native/
  crates/
  docs/
  evals/
  examples/
  tests/
  tools/
  scripts/
  release/
  archive/
  external/
```

This is better than the proposed generic root list.

## Root meanings

| Root         | Meaning                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------ |
| `contracts/` | Product law: semantic models, routes, views, actions, policies, representations.           |
| `runtime/`   | Python reference implementation: kernels, stores, source action, surface rendering, relay. |
| `surfaces/`  | Product-facing projections: web, API, CLI, text, files, lite, native.                      |
| `site/`      | Static public site source and generated static artifact boundary.                          |
| `snapshots/` | Offline/signed/read-only snapshot examples and schemas.                                    |
| `examples/`  | Public-safe fixtures, examples, packs, source examples, golden-ish samples.                |
| `tests/`     | Verification: contract, compatibility, representation, policy, runtime, surface.           |
| `tools/`     | Real implementation tools.                                                                 |
| `scripts/`   | Thin compatibility wrappers only.                                                          |
| `control/`   | Governance, inventories, audits, policies, queue state.                                    |
| `.aide/`     | AI/operator control plane, not product truth.                                              |
| `release/`   | Release/deployment definitions only.                                                       |
| `archive/`   | Retired/quarantined/superseded material only.                                              |
| `external/`  | Pinned external references and upstream notes.                                             |

Do **not** add top-level `renderers`, `skins`, `services`, `apps`, `data`, or `infra`. They become long-term junk drawers.

---

# 2. Where TSIS should live

## Semantic contracts

Add:

```text
contracts/semantic/
  entity.v0.json
  status.v0.json
  badge.v0.json
  affordance.v0.json
  navigation.v0.json
  relationship.v0.json
```

Purpose:

```text
one product language
one status vocabulary
one action vocabulary
one evidence/state grammar
```

This is the long-lived heart of TSIS.

---

## View contracts

Add or converge toward:

```text
contracts/view/
  search_page/
  result_card/
  object_page/
  need_page/
  candidate_page/
  source_page/
  pack_page/
  task_page/
  evidence_page/
  review_page/
  compare_page/
  account_page/
  status_page/
```

The page is not source truth. The **view model contract** is source truth for renderers.

---

## Representation contracts

Add:

```text
contracts/representation/
  representation_profile.v0.json
  renderer_contract.v0.json
  skin_contract.v0.json
  compatibility_budget.v0.json
  fallback_rule.v0.json
  cache_key.v0.json
```

This makes `html32`, `text`, `terminal`, `rich`, `native_card`, and `agent_context` testable, not vibes.

---

## Surface Kernel implementation

Add:

```text
runtime/surface/
  kernel.py
  route_resolver.py
  capability_negotiator.py
  view_model_loader.py
  renderer_dispatch.py
  cache_key.py
  output_policy.py
  fallback.py
  renderers/
    json/
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
```

Important distinction:

```text
runtime/surface/   = machinery
surfaces/          = user-facing adapters
contracts/surface/ = law
```

That avoids mixing implementation with projection packages.

---

## Skins

Do not create top-level `skins/`.

Use:

```text
site/assets/skins/
examples/skins/
contracts/representation/skin_contract.v0.json
```

A skin is authored presentation payload. It is not runtime truth.

---

# 3. How future work fits

## `SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01`

This remains the immediate validation/gating task, not a TSIS task.

It should follow the new policy:

```text
focused validators/tests in AI
external full discovery through harness or CI
AI reads compact full_unittest_summary.json only
```

The queue explicitly says to create an external full-discovery handoff, stop with `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`, and resume only after `full_unittest_summary.json`; it forbids running full discovery inside AI. 

The runbook says the local harness writes compact summary artifacts under `.aide.local/test-runs/<run-id>/` and that `.aide.local/` must not be committed. 

---

## `TSIS-00`

Add doctrine and contracts only:

```text
docs/architecture/TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md
docs/architecture/SURFACE_KERNEL.md
contracts/semantic/
contracts/representation/
contracts/view/
contracts/action/
contracts/route/
contracts/policy/
control/audits/tsis-00-v0/
```

No renderer implementation yet.

---

## `TSIS-01`

Add runtime surface kernel:

```text
runtime/surface/kernel.py
runtime/surface/route_resolver.py
runtime/surface/capability_negotiator.py
runtime/surface/view_model_loader.py
runtime/surface/renderer_dispatch.py
runtime/surface/cache_key.py
runtime/surface/output_policy.py
```

Tests:

```text
tests/runtime/test_surface_kernel.py
tests/contract/test_surface_kernel_contracts.py
tests/policy/test_surface_output_policy.py
```

---

## `TSIS-02`

Add canonical view models:

```text
contracts/view/search_page/
contracts/view/result_card/
contracts/view/object_page/
contracts/view/need_page/
contracts/view/candidate_page/
contracts/view/source_page/
contracts/view/evidence_page/
contracts/view/status_page/
```

Runtime builders:

```text
runtime/surface/view_models/
  search_page.py
  result_card.py
  object_page.py
  need_page.py
```

---

## `TSIS-03`

Add first renderers:

```text
runtime/surface/renderers/json/
runtime/surface/renderers/text/
runtime/surface/renderers/html2/
runtime/surface/renderers/classic_search/
runtime/surface/renderers/rich/
```

Reasonable order:

```text
json    proves contract shape
text    proves semantic fallback
html2   proves durability
classic proves usable old-browser UX
rich    proves modern enhancement
```

---

## `TSIS-04`

Add golden cross-render tests:

```text
tests/golden/representation/
tests/compatibility/representation/
```

Required invariants:

```text
no renderer invents facts
no renderer hides candidate/verified/need state
no renderer exposes forbidden actions
all renderers show evidence summary
all renderers obey output policy
all renderers obey budget
unknown fields degrade safely
```

---

# 4. File and function naming

## Contract files

Use the repo’s current convention unless there is a strong reason to switch.

Recommended:

```text
contracts/semantic/entity.v0.json
contracts/semantic/status.v0.json
contracts/action/action_registry.v0.json
contracts/representation/representation_profile.v0.json
contracts/view/search_page/search_page.v0.json
```

Avoid:

```text
final.json
new_schema.json
view2.json
classic_stuff.json
misc.json
```

## Runtime files

Use role names:

```text
kernel.py
route_resolver.py
capability_negotiator.py
view_model_loader.py
renderer_dispatch.py
cache_key.py
output_policy.py
fallback.py
```

Renderer modules:

```text
render_json.py
render_text.py
render_html2.py
render_html32.py
render_classic_search.py
render_rich.py
```

Avoid:

```text
utils.py
helpers.py
common.py
misc.py
new_renderer.py
legacy_renderer.py
```

## Function names

Use precise verbs:

```text
resolve_route()
negotiate_capability()
load_view_model()
select_renderer()
dispatch_renderer()
build_cache_key()
enforce_output_policy()
render_representation()
apply_fallback_rule()
```

Avoid vague functions:

```text
process()
handle()
do_stuff()
run_it()
manager()
helper()
```

`handle_request()` is acceptable at a boundary adapter, but not as core domain logic.

## IDs and stable vocabulary

Use lower snake case:

```text
verified
candidate
need
near_miss
mention_only
policy_blocked
private_local
superseded
rejected
unknown

download_manifest
review_candidate
report_risk
install_handoff
```

Do not use unstable synonyms in machine fields:

```text
maybe
draft
unconfirmed
provisional
candidate-ish
semi_verified
```

---

# 5. Can this be better?

Yes, but only by adding **governance and tests**, not by adding more roots.

The biggest improvements are:

```text
semantic registries
surface kernel
renderer registry
capability negotiation
representation budgets
golden cross-render tests
accessibility-as-contract
legacy security policy
unknown-field compatibility rules
```

Not:

```text
more directories
more app roots
more UI packages
more one-off renderers
more vertical source scripts
```

The structure should grow by adding **contracts and tested plugins inside stable roots**, not by adding new root concepts.

---

# 6. How this structure outlives the current goals

It outlives the current goals because it is organized around **stable invariants**, not current client types.

## If public alpha changes

You add or alter:

```text
surfaces/web/
surfaces/api/
site/
runtime/gateway/
```

You do not change object identity, evidence, source, or action semantics.

## If native clients become real

You add:

```text
native/
surfaces/native/
runtime/surface/renderers/native_card/
contracts/native/
```

You do not fork search/evidence logic.

## If a terminal or 1990s browser client matters

You add:

```text
runtime/surface/renderers/terminal/
runtime/surface/renderers/html32/
tests/compatibility/representation/
```

You do not create a separate product.

## If AI agents become consumers

You add:

```text
runtime/surface/renderers/agent_context/
contracts/representation/agent_context_profile.v0.json
```

You do not invent an AI-specific truth model.

## If source expansion grows

You add:

```text
runtime/connectors/<family>/
contracts/source/families/<family>.v0.json
examples/sources/<family>/
```

You do not change result page semantics.

## If snapshots become the public distribution unit

You add:

```text
contracts/snapshot/
runtime/snapshot/
runtime/relay/
snapshots/examples/
site/data/
```

You do not change the semantic model.

That is the point: **goals can change; contracts remain the coordination layer.**

---

# 7. Current risk to avoid

The main risk is creating parallel systems:

```text
rich web logic
classic web logic
terminal logic
native logic
agent logic
```

TSIS prevents that only if renderers are pure:

```text
view_model + profile + skin + policy_context
→ representation
```

A renderer must not:

```text
query sources
mutate index
promote candidates
infer evidence
decide policy
invent facts
```

That should be a hard test.

---

# 8. One practical implementation prompt

Use this after the current source/snapshot closeout is resolved.

```text
TSIS-00 — Temporal Semantic Interface Doctrine and Contracts

Goal:
Add the first Temporal Semantic Interface System doctrine and machine-readable
contracts without changing runtime behavior.

Deliverables:
1. Add docs/architecture/TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md.
2. Add docs/architecture/SURFACE_KERNEL.md.
3. Add semantic contracts:
   - contracts/semantic/entity.v0.json
   - contracts/semantic/status.v0.json
   - contracts/semantic/affordance.v0.json
   - contracts/semantic/badge.v0.json
   - contracts/semantic/navigation.v0.json
4. Add representation contracts:
   - contracts/representation/representation_profile.v0.json
   - contracts/representation/renderer_contract.v0.json
   - contracts/representation/skin_contract.v0.json
   - contracts/representation/compatibility_budget.v0.json
   - contracts/representation/fallback_rule.v0.json
5. Add view contract stubs:
   - contracts/view/search_page/search_page.v0.json
   - contracts/view/result_card/result_card.v0.json
   - contracts/view/object_page/object_page.v0.json
   - contracts/view/need_page/need_page.v0.json
   - contracts/view/candidate_page/candidate_page.v0.json
   - contracts/view/source_page/source_page.v0.json
   - contracts/view/evidence_page/evidence_page.v0.json
   - contracts/view/status_page/status_page.v0.json
6. Add registries:
   - control/inventory/semantic_status_registry.json
   - control/inventory/semantic_affordance_registry.json
   - control/inventory/representation_profile_registry.json
7. Add validators and focused tests.
8. No runtime behavior changes.
9. No public alpha.
10. No full unittest discovery inside AI.

Validation:
- focused contract validator tests
- architecture boundaries
- eureka_test_select changed/failed-first
- generated artifact cleanliness

Status:
PASS_WITH_WARNINGS allowed only if full discovery remains externalized.
```

---

# 9. Final answer

Yes, this is close to the best possible structure.

The best version is **not** a bigger root tree. It is:

```text
contracts/      meaning
runtime/        kernels and implementation
surfaces/       projections
site/           static public output
snapshots/      offline/read-only distribution
examples/       public-safe fixtures
tests/          proof
control/        governance
tools/scripts   operators
```

TSIS should be added **inside** that structure:

```text
contracts/semantic/
contracts/representation/
contracts/view/
runtime/surface/
runtime/surface/renderers/
tests/compatibility/representation/
tests/golden/representation/
site/assets/skins/
```

That will outlive the current goals because it decouples:

```text
identity from rendering
policy from UI
evidence from pages
actions from widgets
source adapters from result semantics
client capabilities from product logic
```

That is the structure to keep.
