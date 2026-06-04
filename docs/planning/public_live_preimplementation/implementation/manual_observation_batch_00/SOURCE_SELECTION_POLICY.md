# Source Selection Policy

Task ID: `MANUAL-OBSERVATION-BATCH-00`

## Policy

This batch used bounded, page-level manual references only.

Allowed:

```text
public support pages
public product documentation pages
public hardware reference pages
public author/article pages
metadata/support observations
```

Forbidden and not performed:

```text
downloads
file fetches
Wayback replay
unbounded crawling
full Archive.org integration
product runtime source calls
review promotion
index mutation
```

## Sources Selected

| Source | Use | Posture |
|---|---|---|
| Mozilla support, Firefox Windows 7/8/8.1 | Windows 7 app candidate | metadata support only |
| FlashFXP product and requirements pages | XP FTP near_miss | metadata support only |
| DOS Days CT1740 page | CT1740 manual unavailable state | metadata support only |
| Mozilla support, Firefox XP/Vista | Firefox XP candidate | metadata support only |
| Dick Pountain author page | 1994 Byte ray tracing article candidate | metadata support only |

The Windows 98 driver query intentionally has no source reference because the
query lacks hardware identity.
