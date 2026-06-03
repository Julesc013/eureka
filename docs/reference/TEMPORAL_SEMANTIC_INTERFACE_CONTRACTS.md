# Temporal Semantic Interface Contracts

TSIS-00 introduces these contract families:

- `contracts/semantic/entity.v0.json`
- `contracts/semantic/status.v0.json`
- `contracts/semantic/affordance.v0.json`
- `contracts/semantic/badge.v0.json`
- `contracts/semantic/navigation.v0.json`
- `contracts/semantic/relationship.v0.json`
- `contracts/action/action_registry.v0.json`
- `contracts/route/route_model.v0.json`
- `contracts/representation/renderer_contract.v0.json`
- `contracts/representation/skin_contract.v0.json`
- `contracts/representation/compatibility_budget.v0.json`
- `contracts/representation/fallback_rule.v0.json`
- `contracts/representation/cache_key.v0.json`
- `contracts/view/search_page/search_page.v0.json`
- `contracts/view/result_card/result_card.v0.json`
- `contracts/view/object_page/object_page.v0.json`
- `contracts/view/need_page/need_page.v0.json`
- `contracts/view/candidate_page/candidate_page.v0.json`
- `contracts/view/source_page/source_page.v0.json`
- `contracts/view/evidence_page/evidence_page.v0.json`
- `contracts/view/status_page/status_page.v0.json`

## Canonical Status Vocabulary

Stable status fields use:

- `verified`
- `candidate`
- `need`
- `near_miss`
- `mention_only`
- `policy_blocked`
- `private_local`
- `superseded`
- `rejected`
- `unknown`

Display labels can vary, but machine status should not.

## Canonical Affordances

Stable affordance IDs include:

- `open`
- `inspect`
- `compare`
- `cite`
- `download_manifest`
- `review_candidate`
- `promote`
- `reject`
- `report_risk`
- `preserve`

The policy engine decides action posture. Renderers only express it.

## Forward Compatibility

Unknown fields are not fatal to old clients. Unknown actions should degrade as
unsupported text. Unknown badges should render as labels. Unknown evidence types
should be linked or listed, not interpreted as verified truth.
