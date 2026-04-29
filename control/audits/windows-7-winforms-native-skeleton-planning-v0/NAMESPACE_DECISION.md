# Namespace Decision

Proposed future root namespace:

```text
Eureka.Clients.Windows.WinForms
```

Rationale:

- `Eureka` matches the project identity.
- `Clients` separates future native clients from runtime and surface internals.
- `Windows` names the platform family.
- `WinForms` names the UI technology without encoding a single OS version.

No C# namespace or source file is created by this milestone.

