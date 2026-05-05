# Static Site Evidence

| check | url | status | http | content type | notes |
| --- | --- | --- | --- | --- | --- |
| root | https://julesc013.github.io/eureka/ | verified_failed | 404 | text/html; charset=utf-8 | HTTP 404 |
| search_page | https://julesc013.github.io/eureka/search.html | verified_failed | 404 | text/html; charset=utf-8 | HTTP 404 |
| search_config | https://julesc013.github.io/eureka/data/search_config.json | verified_failed | 404 | text/html; charset=utf-8 | HTTP 404 |
| public_index_summary | https://julesc013.github.io/eureka/data/public_index_summary.json | verified_failed | 404 | text/html; charset=utf-8 | HTTP 404 |

Static URL source: repo config. The URL was checked and classified `verified_failed` because all required static routes returned 404. Operator action: enable or repair Pages/static hosting, record the deployed URL, then rerun the verifier with `--static-url`.
