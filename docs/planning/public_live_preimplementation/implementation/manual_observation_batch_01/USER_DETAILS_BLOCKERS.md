# User Details Blockers

The Windows 98 driver query remains blocked.

Required details:

- hardware vendor
- hardware model
- device ID or chipset
- bus/interface
- exact Windows version
- architecture
- machine or board model
- known source/media context, if any

Safe next action:

```text
ask_for_hardware_details_or_collect_device_identifiers
```

Forbidden action:

```text
recommend_a_specific_driver
```

The secondary task `USER-HARDWARE-DETAILS-00` remains appropriate if this blocker is prioritized.
