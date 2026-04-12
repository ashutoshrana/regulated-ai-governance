# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| 0.1.x   | No        |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

To report a security vulnerability, please use the [GitHub Security Advisory](../../security/advisories/new) feature, or email the maintainer directly.

You should receive a response within 72 hours. If you do not, please follow up to ensure your message was received.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Disclosure Policy

- We will confirm receipt within 72 hours
- We will provide an initial assessment within 7 days
- We aim to release a patch within 30 days of confirmed vulnerability
- We will coordinate with you on the disclosure timeline
- Credit will be given in the release notes unless you prefer anonymity

## Notes on Scope

This library implements **AI agent policy enforcement** for FERPA, HIPAA, and GLBA regulated environments. The security surface is:
- Policy rule evaluation — logic determining whether an agent action is permitted or denied
- Input validation in compliance interceptors (data_category, actor_role, resource_id fields)
- Audit record generation and log output — ensure no PII or PHI leaks into log lines
- Policy bypass edge cases — conditions where enforcement might be silently skipped
- Optional dependency imports (lazy import safety for LLM agent framework integrations)

This library does **not** manage authentication, network access, or cryptography directly. Integrating applications are responsible for securing LLM API keys, agent runtime credentials, and user identity context.

**Regulatory Note:** If you discover a bypass in FERPA, HIPAA, or GLBA policy enforcement logic — even theoretical — treat it as a **critical** vulnerability and report immediately via the Security Advisory channel. Do not publish proof-of-concept code publicly.
