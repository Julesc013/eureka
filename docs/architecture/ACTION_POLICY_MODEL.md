# Action Policy Model

Action policy lives under `control/inventory/actions/` and governs which action families can produce J0 manifests.

The runtime reads policy to decide whether an action family is safe or blocked. Safe families produce descriptive manifests. Risky or unknown families produce blocked reports.

The policy model also defines:

- allowed and forbidden outputs
- allowed output roots
- truth boundary booleans that must remain false
- future risky action gates

Policy does not create product behavior. Runtime helpers remain local, deterministic, and stdlib-only.
