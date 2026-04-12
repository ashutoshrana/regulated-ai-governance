# ADR-004: Framework-Agnostic Compliance Core with Thin Framework Adapters

**Status:** Accepted  
**Date:** 2026-04-12  
**Deciders:** Ashutosh Rana

## Context

Regulated AI governance tooling must work across the ecosystem of agent frameworks in active use: CrewAI, AutoGen, LangChain, Semantic Kernel, and Haystack each have significant enterprise adoption in different verticals (healthcare, financial services, higher education). No single framework dominates; enterprise teams frequently run multiple frameworks in the same organization, and sometimes in the same pipeline.

Two structural options were considered:

1. **Framework-coupled design:** Build the compliance engine as an extension module for a specific framework (e.g., a LangChain `BaseCallback` subclass). Re-implement for each additional framework.
2. **Framework-agnostic core with thin adapters:** The policy engine, regulation objects, and audit logger have zero framework imports. Adapters in `adapters/<framework>.py` translate framework-specific hooks to core API calls.

## Decision

The compliance core (`PolicyEngine`, `ActionPolicy`, `ComplianceViolationError`, `AuditLogger`) contains no imports from any agent framework. All framework coupling is isolated in thin adapter modules under `adapters/`. The core is tested independently of any framework.

## Rationale

**Framework churn is the primary risk:**

The AI agent framework space is less than three years old and has already seen multiple breaking API revisions (LangChain 0.1 → 0.2 callback restructure; AutoGen 0.2 → 0.4 agent model rewrite; CrewAI 0.x → 1.x tool interface change). A compliance library that tightly couples to any one framework's internals faces forced rewrites on every framework major version, with those rewrites landing as breaking changes for consumers.

A framework-agnostic core insulates the compliance logic from this churn. The policy engine for FERPA, HIPAA, or GLBA is stable — the regulation's requirements do not change with CrewAI's release cycle.

**Auditability requires portability:**

In regulated environments, the audit log format must be consistent regardless of which framework produced the agent action. If FERPA audit records from a LangChain-based agent have a different schema than records from a CrewAI-based agent, compliance reporting requires per-framework log parsers. A framework-agnostic `AuditRecord` type, written to by all adapters through a common `AuditLogger` interface, produces a uniform audit trail.

**Test isolation:**

Compliance logic is the most critical path in the library — a policy bypass is a regulatory violation. If compliance tests require a real CrewAI or AutoGen installation, CI becomes fragile (framework install failures cause compliance test failures) and slow (large framework installs on each CI run). With a framework-agnostic core, the policy engine's full test suite runs with zero framework dependencies in under two seconds.

**Multi-framework enterprise deployments:**

A healthcare organization may use LangChain for retrieval pipelines and CrewAI for multi-agent scheduling, both subject to HIPAA. The HIPAA `PHIScope` object and `MinimumNecessaryPolicy` must be sharable across both frameworks without duplication. A framework-agnostic core makes this natural.

## Consequences

**Positive:**
- Adding a new framework adapter (e.g., Haystack, Autogen v5) requires writing one file in `adapters/` and adding an optional dependency — the compliance core is untouched.
- Core unit tests are fast and framework-install-free.
- A single `AuditRecord` schema covers all frameworks, enabling unified SIEM integration.

**Negative:**
- The adapter pattern means framework-specific features (e.g., LangChain's streaming callback chain, AutoGen's group chat message routing) must be mapped to the core API by the adapter author. If a framework introduces a novel execution model with no analog in the core API, the adapter may need to approximate the compliance check rather than integrate perfectly.
- Consumers who use only one framework carry a small overhead: they import the adapter layer in addition to the core. For a compliance library this overhead (~2 files, ~200 lines) is immaterial.

**Neutral:**
- The `adapters/` package is structured so each adapter file is independently importable. A consumer using only CrewAI never loads the AutoGen adapter, and vice versa. This prevents unnecessary import of framework packages the consumer has not installed.
