# Copilot Instructions — regulated-ai-governance

## Project Purpose
`regulated-ai-governance` is a Python library of AI governance filters for multi-agent systems. It provides pre-invocation policy checks, human oversight gates, and audit logging to satisfy EU AI Act, FERPA, HIPAA, GDPR, GLBA, and OWASP Agentic AI Top 10 requirements across multiple agent frameworks (LangChain, CrewAI, AutoGen, Google ADK).

## Core Concepts
- **ComplianceGate** — pre-execution policy check at every agent action boundary; DENIED = action blocked before invocation
- **Google ADK Adapter** — 757-line implementation at `adapters/google_adk_adapter.py`; enforces Art. 14 override right via pre-tool-invocation hook
- **Ordered Safety Policy Broker (OSPB)** — priority-ordered policy evaluation; first DENIED policy wins
- **Regulatory Context Injection (RCI)** — injects applicable regulations into agent context based on data type and jurisdiction
- **Human-Oversight Escalation Chain (HOEC)** — multi-tier escalation: tool retry → human review → supervisor override

## Package Structure
```
src/regulated_ai_governance/
  gate.py            — ComplianceGate, PolicyBroker
  adapters/
    google_adk_adapter.py   — Google ADK (757 lines, commit 4817d64)
    langchain_adapter.py
    crewai_adapter.py
    autogen_adapter.py
  policies/          — regulation-specific policy classes
  audit.py           — session-close audit log
examples/
  google_adk_compliance_gate.py
  langchain_compliance_gate.py
articles/
  eu-ai-act-agents-developer-guide.md   — dev.to article (canonical source)
tests/
  test_gate.py, test_adapters/, test_policies/
```

## Code Conventions
- Every tool invocation gate must produce an audit log entry: timestamp, session_id, tool_name, policy_applied, decision, regulation_citation
- Adapters must be framework-isolated — no cross-adapter imports
- `ComplianceGate.evaluate()` is synchronous; async variants in `adapters/` use `async_evaluate()`
- Tests use `pytest`; 84 tests for Google ADK adapter specifically

## Regulatory Citations
- EU AI Act Art. 9 — risk management; Art. 12 — logging; Art. 13 — transparency; Art. 14 — human oversight; Art. 15 — accuracy/robustness
- OWASP Agentic AI Top 10 — ASI-09 (confidence-gated dispatch), ASI-01 (prompt injection), ASI-03 (privilege escalation)
- FERPA 34 CFR Part 99 — education record protection in AI pipelines
- HIPAA 45 CFR 164 — PHI in clinical AI systems
- GDPR Art. 22 — automated decision-making

## What NOT to Include
- No customer/client names (SEI, Capella, Strayer) or product names (ELLA, Falcon, Polaris, ASTRUM, JARVIS)
- No production GCP project IDs, API keys, or cloud-specific configs
- Framework adapters must be installable independently of each other
- No agent task definitions specific to any enterprise use case

## PR Standards
- PR title: conventional commits — `feat: add Smolagents adapter` / `fix: GDPR Art.22 automated decision check`
- New adapter = implementation + tests (minimum 20) + README entry + examples/
- Use the `.claude/skills/add-governance-filter.md` skill for step-by-step guidance
