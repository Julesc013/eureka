# Repair Decision

The failure is classified as `local_python_trust_store`.

No safe repo-side transport bug was found. The existing transport uses HTTPS,
SNI through the hostname, Python's verified default SSL behavior, User-Agent and
contact headers, and request caps.

No repo script should mutate the machine trust store. The operator action is to
repair Python's local certificate trust configuration, then rerun IA-02 with
the same approved bounded command.

IA-03 remains blocked until a successful approved IA metadata response exists.
