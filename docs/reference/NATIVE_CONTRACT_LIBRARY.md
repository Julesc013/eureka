# Native Contract Library

The C89 contract library under `native/lib/c89/` provides bounded helper functions for native clients.

Current scope:

- status codes and status names
- bounded string and token helpers
- snapshot manifest marker helpers
- relay status marker helpers
- action manifest marker helpers

It is not a full JSON parser. It performs no file I/O, network access, download, install, execution, emulation, or GUI work. Callers provide all buffers.

Validation:

```powershell
python scripts/validate_native_c89_library.py
```
