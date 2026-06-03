# Public Pages V1

Minimum public page set:

- `/`
- `/search`
- `/object/{id}`
- `/candidate/{id}`
- `/need/{id}`
- `/source/{id}`
- `/evidence/{id}`
- `/status`
- `/about`
- `/method`

Existing public-alpha routes may use `/alpha` prefixes or API equivalents. A
future route migration must preserve read-only posture and status visibility.

Each page must expose canonical status, evidence posture, allowed actions,
blocked actions where relevant, and uncertainty/absence when relevant.

