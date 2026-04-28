# Public Route Stability

Route stability is controlled by
`control/inventory/publication/publication_contract.json` and used by
`page_registry.json`.

`experimental`: May change while publication contracts are still pre-alpha.

`stable_draft`: Intended to persist, but still subject to review before stable
status.

`stable`: Durable public route or data contract. Changes require a deprecation
path.

`deprecated`: Still present, but scheduled for removal or replacement.

`removed`: No longer present in the active public contract.

No route should move to `stable` until its base-path behavior, claim source,
client profile, public data dependencies, and redirect/deprecation story are
clear.

Custom-domain readiness does not make a route stable. A route that works under
both `/eureka/` and `/` may still remain `stable_draft` until public data,
redirect, and deprecation policies mature.

Live backend handoff readiness does not make `/api/v1` stable or live. The
reserved `/api/v1` route family stays `experimental` until a later hosted
backend milestone defines and verifies runtime behavior.
