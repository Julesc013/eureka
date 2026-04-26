from __future__ import annotations

USER_COST_SCALE = {
    0: "direct verified artifact / immediately actionable bounded result",
    1: "inner member with path, evidence, lineage, and bounded action hints",
    2: "direct representation with source evidence but no member-level detail",
    3: "bundle or representation with member-listing context",
    4: "parent bundle context only",
    5: "documentation, readme, manual, or compatibility-note support",
    6: "mention-only trace",
    7: "unresolved absence or next-step only",
    8: "wrong object type or demoted interpretation",
    9: "unknown or high-cost result",
}
