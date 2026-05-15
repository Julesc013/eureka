# Local Shutdown And Clean State

After a LOCAL smoke run:

```powershell
python scripts/eureka_lan_shutdown_check.py --instance ./eureka-instance --port 8765 --json
git status --short
```

Expected state:

- the server is no longer serving Eureka on the checked port
- the instance still validates
- `eureka-instance/` remains ignored and uncommitted
- no `site/dist` mutation occurred
- no master index mutation occurred
- no deployment occurred

Local DB/log/run/tmp files belong only under the explicit instance path.
