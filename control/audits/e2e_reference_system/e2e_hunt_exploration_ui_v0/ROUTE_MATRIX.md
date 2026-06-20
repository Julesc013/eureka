# Route Matrix

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/explore` | Preview workspace HTML |
| GET | `/api/v1/explore` | Preview workspace JSON |
| GET | `/explore/runs` | Durable run list HTML |
| GET | `/api/v1/explore/runs` | Durable run list JSON |
| GET | `/explore/run/<run-id>` | Durable run detail HTML |
| GET | `/api/v1/explore/run/<run-id>` | Durable run detail JSON |
| GET | `/explore/compare` | Read-only compare HTML |
| GET | `/api/v1/explore/compare` | Read-only compare JSON |
| POST | `/explore/run/start` | Operator-token synthetic run start |
| POST | `/api/v1/explore/run/start` | Operator-token synthetic run start |
| POST | `/explore/run/<run-id>/replay` | Operator-token bundle replay |
| POST | `/explore/run/<run-id>/(pause|resume|cancel|step)` | Operator-token controls; terminal synthetic runs block safely |

