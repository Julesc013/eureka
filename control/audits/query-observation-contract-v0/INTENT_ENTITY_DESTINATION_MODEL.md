# Intent Entity Destination Model

P59 records coarse intent rather than authoritative truth. Allowed intents
include exact artifact lookup, software version lookup, driver lookup,
documentation lookup, source-code lookup, package metadata lookup, inside
container member lookup, scan article lookup, comparison, compatibility check,
absence explanation, and unknown.

Destination values keep unsafe action intent visible but disabled. Download,
install, execute, upload, emulation, and reconstruction remain blocked actions.

Detected entities are public-safe summaries such as platform, version,
architecture, artifact type, source family, file name, extension, vendor,
package name, or identifier.
