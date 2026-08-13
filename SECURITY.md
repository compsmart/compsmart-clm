# Security policy

Please report security issues privately through GitHub's security advisory
feature for this repository. Do not place vulnerabilities, service secrets, or
extracted confidential material in a public issue.

The public endpoint deliberately exposes a narrow text-only interface plus
read-only model/runtime telemetry and learner-owned history, verification, and
reload controls. File uploads, arbitrary URL retrieval, tool execution,
secrets, system prompts, raw state files, and unrestricted internal diagnostics
are not exposed. Attempts to extract confidential model material or bypass
learner isolation are prohibited.

Published verification clients must never contain credentials. If a secret is
found in repository history, treat it as compromised and report it immediately.
