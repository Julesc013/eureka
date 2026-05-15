# Local LAN Shutdown And Cleanup

After a LAN smoke run:

1. Stop the server process.
2. Check the port is no longer serving Eureka.
3. Validate the explicit local instance.
4. Confirm no local instance state is committed.

Command:

```powershell
python scripts/eureka_lan_shutdown_check.py --instance ./eureka-instance --port 8765 --json
```

Logs may exist only under the explicit instance root. Do not commit
`eureka-instance/**`.
