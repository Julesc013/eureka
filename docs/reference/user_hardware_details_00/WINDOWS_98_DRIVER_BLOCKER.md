# Windows 98 Driver Blocker

The Windows 98 driver hard query remains blocked.

```text
query_id: hq_driver_win98
blocker_task: USER-HARDWARE-DETAILS-00
status: blocked_for_user_details
```

## Why This Is Blocked

Windows 98 drivers are hardware-specific. A generic operating-system request is
not enough to identify a safe or compatible driver. Recommending a driver
without device identity can point the user at the wrong chipset, wrong board
revision, wrong bus type, wrong Windows 98 edition, or unsafe install path.

## Required Before Review

- vendor and model of the device or board
- chipset or controller family
- device id, if available
- bus/interface type
- exact Windows 98 version
- machine or motherboard context
- source/media context for any candidate driver

## Current Boundary

No specific Windows 98 driver should be recommended until the details packet is
returned and reviewed. Source leads may be collected later, but they must stay
non-promoted until the hardware identity is known.
