# F0 Blocked Actions

F0 blocks unsafe actions by default:

- download
- upload
- filesystem extraction
- arbitrary file extraction
- execution
- install
- emulation
- model/provider calls
- source-cache or evidence writes
- candidate/review/reviewed-index mutation
- master/public index mutation
- deployment

The foundation is fixture-only and manifest-only. It is not truth and requires review for any future use of member observations. Unsafe containers, path traversal, absolute paths, nested archives, symlinks, device files, encrypted archives, executable installers, and unknown binary containers remain blocked or deferred.

No downloads, no filesystem extraction, and no execution are mandatory boundaries for this task.
