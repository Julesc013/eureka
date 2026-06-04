# Expected Answer Shapes Report

Task ID: `HARD-QUERY-EVAL-00`

## Shape File

Path:

```text
evals/hard_queries/expected_answer_shapes_v0.json
```

## Shape Rules

The expected answer-shape registry defines useful units plus required and disallowed public output features for each hard query.

Examples:

```text
Windows 7 apps
→ software artifact, compatible installer, portable package, or scoped compatibility need

driver for Win98
→ device-specific driver candidate, hardware identification need, or near miss with platform mismatch

old blue FTP client for XP
→ candidate identity, near miss with missing visual evidence, or need for more clues

manual for Sound Blaster CT1740
→ manual artifact, exact hardware-page candidate, or documentation source need

latest Firefox before XP support ended
→ candidate version/support answer, need for support-window evidence, or policy-blocked degraded result

article about ray tracing in a 1994 magazine
→ article candidate, issue/page need, or scoped unavailable article-scan state
```

## Absence Posture

The eval follows the AbsencePage contract: absence is scoped, not omniscient. Fixtures may represent source gaps, capability gaps, needs, near misses, policy blocks, or unavailable states, but they must not claim exhaustive global search.
