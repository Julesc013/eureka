# LOCAL-01 Local Instance Bootstrap Audit

This audit records LOCAL-01: explicit local appliance instance layout and bootstrap commands.

LOCAL-01 adds operator commands for instance initialization, validation, and read-only status inspection. It creates no server, no HTML workbench, no WorkUnit runtime, no LAN binding, and no deployment.

The audit records a warning because full unittest discovery still fails on the pre-existing runtime leakage gate. LOCAL-01 does not increase that leakage baseline.
