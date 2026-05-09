# Native Matrix Contract

`contracts/native/native_matrix.v0.json` defines the governed native lane matrix for Eureka clients.

The matrix records lane IDs, API/toolchain ownership, host references, future artifact references, consumed contracts, and limitations. Current C-BUNDLE-01 lanes consume snapshot, relay, action, and view contracts only.

The matrix does not authorize live source access, native resolver internals, release binaries, downloads, installers, execution, public index mutation, or master index mutation.

Validation:

```powershell
python scripts/validate_native_matrix.py
```
