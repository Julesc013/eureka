# Search Hunt UI Routes

| Route | Method | Kind | Mutation |
| --- | --- | --- | --- |
| `/hunts` | GET | HTML list | none |
| `/hunt/<hunt_id>` | GET | HTML detail/not-found | none |
| `/api/v1/hunts` | GET | JSON list | none |
| `/api/v1/hunt/<hunt_id>` | GET | JSON detail/not-found | none |

JSON responses include `schema_version`, `status`, `warnings`, and `limitations`. Detail responses include `hunt`, `transitions`, and `summaries`.

HUNT-02 adds no POST route for hunts.

