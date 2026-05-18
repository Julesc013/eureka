# IA-02 TLS Trust Sample Summary

Python TLS verification remains enabled. The local machine cannot complete a
verified TLS handshake to `archive.org` because Python has no usable default CA
file/capath and the chain reports self-signed. No insecure bypass was used and
the approved IA metadata probe was not rerun.
