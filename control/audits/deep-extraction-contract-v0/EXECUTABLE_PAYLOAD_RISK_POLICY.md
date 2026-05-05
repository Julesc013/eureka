# Executable Payload Risk Policy

Executable payload policy requires:

- no execution
- no installer execution
- no package manager invocation
- no emulator or VM launch
- no script execution
- no macro execution
- no binary inspection beyond metadata unless a future sandbox is approved
- executable references labelled `executable_reference` or `malware_review_required`
- `malware_safety_claimed: false`
- payload safety unknown unless separate review exists

Extraction summaries must not make malware safety, script safety, or payload safety claims.
