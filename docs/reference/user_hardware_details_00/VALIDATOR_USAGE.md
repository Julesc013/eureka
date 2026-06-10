# Hardware Details Return Validator

Use this validator before moving the Windows 98 driver query out of
`blocked_for_user_details`.

Default external return path:

```text
../eureka-evidence-runs/user_hardware_details_00/user_hardware_details_return.json
```

Run:

```powershell
python scripts/validate_user_hardware_details_return.py --json --strict
```

Strict mode requires:

- hardware vendor
- hardware model, chipset, FCC ID, or product label text
- at least one PCI, ISA, USB, PCMCIA/CardBus, or other device ID
- where the device ID was observed
- bus or interface
- exact Windows version
- Windows 98 edition
- architecture
- source, media, attachment, or observation context

Passing validation does not recommend a driver, create reviewed artifact truth,
create a verified artifact, prove compatibility, clear rights, or prove malware
safety. It only means the returned user details are structured enough for a
future review task.

