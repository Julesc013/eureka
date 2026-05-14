# Route Matrix

| Route | Method | Auth | Scope | Side effect |
| --- | --- | --- | --- | --- |
| `/hunt/<hunt_id>/commands` | GET | none | local/LAN read-only where enabled | none |
| `/api/v1/hunt/<hunt_id>/commands` | GET | none | local/LAN read-only where enabled | none |
| `/hunt/<hunt_id>/steering` | GET | none | local/LAN read-only where enabled | none |
| `/api/v1/hunt/<hunt_id>/steering` | GET | none | local/LAN read-only where enabled | none |
| `/hunt/<hunt_id>/pause` | POST | operator token | localhost only | hunt state and command history |
| `/hunt/<hunt_id>/resume` | POST | operator token | localhost only | hunt state and command history |
| `/hunt/<hunt_id>/cancel` | POST | operator token | localhost only | hunt state and command history |
| `/hunt/<hunt_id>/block` | POST | operator token | localhost only | hunt state and command history |
| `/hunt/<hunt_id>/wait-for-user` | POST | operator token | localhost only | hunt state and command history |
| `/hunt/<hunt_id>/wait-for-policy` | POST | operator token | localhost only | hunt state and command history |
| `/hunt/<hunt_id>/steer` | POST | operator token | localhost only | steering and command history |
