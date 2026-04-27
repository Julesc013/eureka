# Task-by-Task Refinement

| Task | Baseline | Current | Why |
| --- | --- | --- | --- |
| `driver_inside_support_cd` | partial | satisfied | Primary result is a source-backed member, `drivers/wifi/thinkpad_t42/windows2000/driver.inf`, with driver/member shape, requested hardware/platform evidence, expected lane fit, and no accepted bad pattern. |
| `latest_firefox_before_xp_drop` | partial | partial | Firefox and Windows XP support evidence exists, but exact latest-compatible release identity and direct release asset evidence are not proven. |
| `old_blue_ftp_client_xp` | partial | partial | FTP and Windows XP evidence exists, but the result remains a bundle/trace and does not prove a concrete product identity or direct installer. |
| `win98_registry_repair` | partial | partial | Registry-repair and Windows 98 evidence exists, but the primary lane is preservation/context rather than best-direct or installable. |
| `windows_7_apps` | partial | partial | Direct application representation evidence exists, but lane/user-cost still treats the result as inside-bundle/context rather than installable/best-direct. |
| `article_inside_magazine_scan` | capability_gap | capability_gap | No bounded scan/OCR/article/page fixture evidence exists. |

No task definition was weakened. No task was removed. Satisfaction is allowed
only when search evidence, primary result shape, lane expectation, and
bad-result checks all pass.
