# LOCAL-11 LAN Binding Safety Gate

This audit records the LAN binding policy and safety gate for the Local Appliance.

LOCAL-11 adds an explicit `--bind-lan` guard and read-only LAN route policy. It
does not perform the actual cross-device LAN smoke test, deploy a service, run
source probes, execute WorkUnits from LAN, or make production/public launch
claims.
