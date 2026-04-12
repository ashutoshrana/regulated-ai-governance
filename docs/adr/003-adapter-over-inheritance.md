# ADR-003: Adapter Pattern over Inheritance for Framework Integration

**Status:** Accepted  
**Date:** 2026-04-12  
**Deciders:** Ashutosh Rana

## Context

When integrating compliance policy enforcement with AI agent frameworks (CrewAI, AutoGen, LangChain, Semantic Kernel, Haystack), two structural approaches are available:

1. **Inheritance:** Subclass the framework's base agent or tool class, override lifecycle methods to inject policy checks, and publish these as `FERPACrewAIAgent`, `HIPAAAutoGenAgent`, etc.
2. **Adapter/Wrapper:** Define a thin wrapper class that holds a reference to the framework object and delegates to it after performing a policy check. The framework class itself is untouched.

The choice has significant downstream consequences for the library's maintenance burden and consumer upgrade path.

## Decision

Use the adapter/wrapper pattern for all framework integrations. Framework classes are wrapped, not subclassed. The compliance core (`PolicyEngine`, `CompliancePolicy`, `AuditLogger`) has no imports from any agent framework. Framework-specific code lives exclusively in `adapters/<framework>.py`.

## Rationale

**Why adapters over inheritance:**

Framework base classes change frequently. CrewAI v0.x to v1.x renamed tool base classes, changed `_run` signatures, and restructured the agent initialization API. AutoGen 0.2 to 0.4 introduced a new `ConversableAgent` architecture. If this library subclasses these base classes, each framework major version requires a subclass rewrite — and those rewrites are breaking changes for consumers who depend on the subclass API.

Adapters are structurally decoupled: the wrapper holds a reference to the framework object and calls `_run()` or `generate_reply()` on it, but it does not depend on the internals of those classes. If the framework renames a method, only the adapter's 10-line delegation block needs updating, not a full subclass override chain.

Duck typing makes this practical: CrewAI tools are duck-typed (they implement `_run`), and AutoGen agents are duck-typed (they implement `generate_reply`). The adapter can wrap any object that satisfies the interface without inheriting from a specific class.

**Why adapter enables lazy imports:**

The compliance core must import cleanly without any framework installed. An `import crewai` at the top of a module that defines `FERPACompliancePolicy` would make crewai a hard dependency of the entire library. With the adapter pattern, `adapters/crewai.py` does a lazy import inside `__init__` or `_run`, isolated behind a try/except that raises a helpful `ImportError` only when the adapter is actually instantiated. This lets teams use the HIPAA policy module without installing CrewAI.

**Why not inheritance:**

Inheritance also creates a naming collision problem. If CrewAI introduces a `BaseTool.validate()` method in a future version, and this library's `EnterpriseActionGuard` subclass defines its own `validate()` for policy validation, the two silently conflict. With an adapter, `EnterpriseActionGuard.validate_policy()` has no naming overlap with the wrapped tool's methods.

## Consequences

**Positive:**
- Framework version upgrades require changes only in `adapters/<framework>.py`, never in the compliance core.
- All framework imports are lazy and optional; installing the library without CrewAI does not cause import errors.
- Unit tests for adapters use duck-typed stubs — no real framework install required in CI for the core test suite.
- The adapter's public API (`EnterpriseActionGuard`, `PolicyEnforcingAgent`) can maintain a stable signature even as the wrapped framework changes its internal API.

**Negative:**
- Adapters cannot override framework lifecycle hooks that are invoked before the public methods reach the adapter (e.g., framework-internal pre-execution hooks). If a framework adds a built-in compliance feature in a future version, the adapter sits beside it rather than composing with it cleanly.
- The consumer must explicitly wrap their tool/agent in the adapter. There is no transparent injection of policy enforcement — the wrapping step is visible in the consumer's code, which some teams find verbose.

**Neutral:**
- Each framework adapter is a separate file and can have its own optional dependency declaration in `pyproject.toml` (e.g., `crewai = ["crewai>=1.0"]`). This is a standard extras pattern and does not require separate packages.
