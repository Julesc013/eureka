# Prohibited Data Review

Public-safe query observations and examples must not include:

- IP address
- account ID
- email address
- phone number
- API key
- auth token
- password
- private key
- private path
- Windows absolute path
- POSIX home path
- private URL
- user-uploaded filenames without consent
- local private result identifiers

The P59 validator rejects obvious private path, private URL, credential, and
secret-like markers in observation string values.
