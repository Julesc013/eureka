# User Hardware Details 00

Task: `USER-HARDWARE-DETAILS-00`

Status: waiting for user-supplied hardware identity details.

This packet records the information required before Eureka can safely review or
recommend a specific Windows 98 driver artifact. It is a blocker-resolution
packet, not a driver recommendation and not evidence that any driver is safe,
compatible, rights-cleared, downloadable, or verified.

## Blocked Query

```text
query_id: hq_driver_win98
status: WAITING_FOR_USER_HARDWARE_DETAILS
```

The query remains blocked because a Windows 98 driver recommendation depends on
the exact hardware identity, bus/interface, and operating-system variant.

## Required Details

- hardware vendor
- hardware model
- chipset
- PCI, ISA, USB, PnP, or other device id if available
- bus or interface
- machine or motherboard model
- exact Windows 98 version and edition
- architecture
- source or media context
- photos, manual labels, FCC IDs, silkscreen labels, or existing driver media
  if available

## Packet Files

- [Windows 98 driver blocker](WINDOWS_98_DRIVER_BLOCKER.md)
- [Hardware details request](HARDWARE_DETAILS_REQUEST.md)
- [Device id capture guide](DEVICE_ID_CAPTURE_GUIDE.md)
- [Safe driver review rules](SAFE_DRIVER_REVIEW_RULES.md)
- [Return template](RETURN_TEMPLATE.json)
- [Validation report](VALIDATION_REPORT.md)

## Resume Rule

After the user supplies enough hardware identity details, a future task may
review the returned details and decide whether the driver query can move from
`blocked_for_user_details` into a reviewable artifact evidence path.

Do not skip directly to a driver recommendation.
