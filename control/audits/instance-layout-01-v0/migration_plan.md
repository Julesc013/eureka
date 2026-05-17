# Migration Plan

Manual operator migration from the legacy sibling path to the canonical path:

```powershell
mkdir D:\Projects\Eureka\instances
move D:\Projects\Eureka\eureka-instance D:\Projects\Eureka\instances\default
```

Then validate from the repo root:

```powershell
cd D:\Projects\Eureka\eureka
python scripts/eureka_validate_instance.py --instance D:\Projects\Eureka\instances\default --json
```

Repository scripts may print or dry-run this plan, but they do not move or
delete the operator's instance automatically.
