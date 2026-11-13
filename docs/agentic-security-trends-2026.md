# Agentic AI security: taxonomy and example boundaries

Reviewed 2026-11-13. This note replaces inaccurate ASI mappings in the earlier
version. It describes local examples, not mandatory OWASP requirements or certification.

## Authoritative taxonomy

Source: [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/),
published 2025-12-09; category identifiers cross-checked against the
[OWASP risk-assessment playbook](https://github.com/OWASP/secure-agent-playbook/blob/main/plugins/ai-security-skills/plays/agentic-ai-risk-assess.md).

| ID | Category | Related local example checks |
|---|---|---|
| ASI01 | Agent Goal Hijack | Injection-detection and sanitisation flags |
| ASI02 | Tool Misuse | Tool allowlist and approval flags |
| ASI03 | Identity & Privilege Abuse | Cross-session privilege flag |
| ASI04 | Agentic Supply Chain Vulnerabilities | Tool signature flag |
| ASI05 | Unexpected Code Execution | No dedicated check |
| ASI06 | Memory & Context Poisoning | Retrieval integrity, anomaly and memory isolation flags |
| ASI07 | Insecure Inter-Agent Communication | Sender-verification flag |
| ASI08 | Cascading Failures | Rollback and oversight flags |
| ASI09 | Human-Agent Trust Exploitation | Capability/confidence disclosure flags |
| ASI10 | Rogue Agents | No dedicated check |

The full report also uses the ASI02 title “Tool Misuse and Exploitation”; the
constant uses the shortened playbook title above. Category mapping does not
establish control effectiveness or complete coverage.

## What example 39 actually does

[`39_owasp_agentic_top10_governance.py`](../examples/39_owasp_agentic_top10_governance.py)
evaluates caller-supplied metadata. It does not perform signature verification,
injection detection, DLP scanning, identity verification, sandboxing, or rollback.
Trusted application components must produce and bind that evidence to an action.
The anomaly/confidence thresholds are demonstration choices, not OWASP mandates.

`LOCAL-DLP` and `LOCAL-AUDIT` identify supplemental output-scanning and audit
policies, not ASI categories. Example class names, inputs and decision predicates
are retained; corrected citation strings are a compatibility change for consumers
that parsed them. See [migration guidance](../MIGRATION.md).

**Not fail-closed:** absent metadata may pass. `REQUIRES_HUMAN_REVIEW` is returned
but is not blocked by the wrappers, which only raise on `DENIED`. Applications
must explicitly stop and route review decisions before execution. The wrappers
are duck-typed examples, not native SDK qualification. The `ainvoke` example is
synchronous despite its name. Do not treat it as an awaitable SDK implementation.

## Sources and reuse

OWASP's [report](https://genai.owasp.org/download/52117/?tmstv=1765059207)
and resource page state [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode)
unless otherwise specified. The category
names/identifiers are attributed above; this table is a project-authored mapping,
not copied OWASP control text. OWASP materials retain their own terms and are not
relicensed by this repository's MIT license. No OWASP endorsement is implied.
See [source register](SOURCES.md) for review scope and maintenance requirements.
