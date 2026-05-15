# LOCAL To HUNT/SYN/F0 Handoff

HUNT, SYN, and F0 may plan from the Local Appliance only after LOCAL-14 records
the handoff inventories.

HUNT starts with `HUNT-00` planning over the Local Appliance, then `HUNT-01`
Search Hunt Session runtime.

SYN starts with `SYN-00` planning over the Local Appliance, then `SYN-01`
synthetic query taxonomy and contracts.

F0 may resume through `F0-00`, but extraction work must use explicit instances,
WorkUnits, source observations, evidence/review/index gates, workbench
visibility, and auto-test proof. LOCAL-14 does not implement F0.
