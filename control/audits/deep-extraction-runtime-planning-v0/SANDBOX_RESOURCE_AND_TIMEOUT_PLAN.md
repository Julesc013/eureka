# Sandbox Resource And Timeout Plan

Future policy values:

- `max_depth`: operator_pending; examples use future depth 3.
- `max_members`: operator_pending; examples use future count 1000.
- `max_total_uncompressed_size`: operator_pending.
- `max_member_size`: operator_pending.
- `max_runtime_ms`: operator_pending; examples use future 5000.
- `max_text_bytes`: operator_pending; examples use future 4096.
- `max_OCR_pages`: 0 by default until OCR approval.
- `allowed_container_kinds`: operator_pending.
- `denied_container_kinds`: executable/install/runtime-risk containers denied by default.
- decompression bomb guard: required.
- zip-slip/path traversal guard: required.
- symlink/hardlink guard: required.
- temporary workspace cleanup: required.
- network disabled: required.
- execution disabled: required.

Because values remain operator_pending, runtime implementation stays blocked.

