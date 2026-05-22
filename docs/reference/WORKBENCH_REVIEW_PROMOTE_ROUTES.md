# Workbench Review Promote Routes

Routes are adapted to the existing local Workbench service style.

| Route | Method | Purpose |
| --- | --- | --- |
| `/review` | GET | Review queue list using existing local review service |
| `/review/{review_item_id}` | GET | Review item detail |
| `/promotion` | GET | Promotion preview projection |
| `/promotion/{preview_id}` | GET | Promotion preview detail projection |
| `/index/rebuild-preview` | GET | Reviewed-index refresh preview |
| `/api/v1/review` | GET | Review queue JSON |
| `/api/v1/review/{review_item_id}` | GET | Review item JSON |
| `/api/v1/review/{review_item_id}/decision` | POST | Operator-gated decision endpoint |
| `/api/v1/promotion-preview` | GET/POST | Promotion preview JSON or operator-gated request |
| `/api/v1/promotion-preview/{preview_id}` | GET | Promotion preview JSON detail |
| `/api/v1/reviewed-index/refresh-preview` | GET/POST | Refresh preview JSON or operator-gated request |

Public and native read-only projections must not submit review or promotion mutations.
