# Privacy And Redaction Policy

Raw query retention default is `none`. Public-safe cache entries must not
contain IP addresses, account identifiers, emails, phone numbers, API keys,
auth tokens, passwords, private keys, private paths, private URLs, private
local result identifiers, or user-uploaded filenames without consent.

If prohibited data is detected, the entry must be rejected by privacy filtering
or redacted before aggregate use. P60 examples are synthetic and not collected
from real users.
