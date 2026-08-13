# Security policy

Please report security issues privately through GitHub's security advisory
feature for this repository. Do not place vulnerabilities, service secrets, or
extracted confidential material in a public issue.

The public endpoint deliberately exposes a narrow text-only interface. File
uploads, arbitrary URL retrieval, tool execution, internal diagnostics, and
implementation disclosure are out of scope for normal use. Attempts to extract
confidential model material or bypass session isolation are prohibited.

Published verification clients must never contain credentials. If a secret is
found in repository history, treat it as compromised and report it immediately.

