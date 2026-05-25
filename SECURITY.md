# Security Policy

Forge Context Engine is a documentation and context-lifecycle foundation. It is not a deploy platform, runtime execution platform, CI/CD runner, or autonomous agent system.

## Reporting Security Concerns

If you find a security issue, please report it privately to the repository maintainer.

Do not open a public issue that includes:

- production credentials
- API keys, tokens, private keys, cookies, or passwords
- credential-bearing URLs
- sensitive customer data
- internal incident details that should not be public

Use sanitized examples whenever possible. If a secret may have been exposed, rotate it before sharing any reproduction details.

## What To Report

Security and governance concerns are welcome, including:

- accidental secret or PII exposure in examples, docs, context, or artifacts
- unsafe guidance around financial correctness, idempotency, retry/replay, rollback, or validation honesty
- wording that could imply autonomous approval of high-risk decisions
- documentation that appears to introduce runtime execution, deploy automation, or hidden persistent memory behavior

## Responsible Disclosure Expectations

- Give maintainers reasonable time to investigate and patch.
- Share only the minimum evidence needed to reproduce or understand the issue.
- Avoid publishing exploit details or sensitive examples before maintainers respond.

Forge's security posture is intentionally lightweight and practical: prevent unsafe context handling, avoid sensitive data exposure, and preserve human approval for high-risk engineering decisions.
