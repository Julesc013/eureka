# Safe Query Verification

| query | route | expected | actual | local_index_only | result/gap behavior | notes |
| --- | --- | --- | --- | --- | --- | --- |
| windows 7 apps | /api/v1/search | 2xx local_index_only response | None | None | None | Hosted backend URL not configured. |
| driver.inf | /api/v1/search | 2xx local_index_only response | None | None | None | Hosted backend URL not configured. |
| pc magazine ray tracing | /api/v1/search | 2xx local_index_only response | None | None | None | Hosted backend URL not configured. |
| no-such-local-index-hit | /api/v1/search | 2xx local_index_only response | None | None | None | Hosted backend URL not configured. |
