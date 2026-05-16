# Failure Register

Nine initial golden failures were diagnosed:

- compact task packet and repo boundary failures from stale, generic generated context.
- release archive, checksum, fixture, forbidden-path, asset, and no-publish failures from missing post-merge export/release artifacts.
- GitHub report-only failure from treating pre-existing target workflow files as an AIDE mutation.

All failures were safe AIDE/control-plane repairs. No Eureka product behavior change was required.

