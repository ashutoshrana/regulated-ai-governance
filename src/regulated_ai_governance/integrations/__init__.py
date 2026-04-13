"""
integrations — Framework integration adapters for regulated AI governance.

Provides policy-enforcement bridge components for popular agentic AI frameworks.
All framework-specific imports are lazy so the package is importable without
any framework dependency installed.

Available integrations
----------------------
- ``EnterpriseActionGuard``     — CrewAI ``BaseTool`` wrapper (crewai>=1.14)
- ``GovernedDSPyModule``        — DSPy ``Module`` wrapper (dspy>=2.5, Pydantic v2)
- ``GovernedDSPyPipeline``      — DSPy sequential pipeline with per-step enforcement
- ``PolicyEnforcingAgent``      — AutoGen agent with inline policy enforcement
- ``PolicyKernelPlugin``        — Semantic Kernel function plugin
- ``PolicyMiddleware``          — Microsoft Agent Framework (MAF) middleware (NEW — MAF 2026)
- ``LangChainPolicyGuard``      — LangChain tool wrapper
- ``GovernedHaystackComponent`` — Haystack 2.x pipeline component (duck-typed)
- ``make_haystack_policy_guard``— Haystack 2.27 ``@component`` factory (NEW)
- ``GovernedQueryEngine``       — LlamaIndex ``QueryEngine`` wrapper
- ``PolicyWorkflowGuard``       — LlamaIndex 0.12+ Workflow guard step (NEW)
- ``PolicyWorkflowEvent``       — LlamaIndex Workflow event type (NEW)

Note on AutoGen and Semantic Kernel:
Both AutoGen and Semantic Kernel are in maintenance mode as of 2026. Microsoft
recommends migrating to Microsoft Agent Framework (MAF). The AutoGen and
Semantic Kernel integrations remain available for backward compatibility, but
new projects should use the MAF integration (``PolicyMiddleware``).
"""

from .dspy import GovernedDSPyModule, GovernedDSPyPipeline
from .haystack import GovernedHaystackComponent, make_haystack_policy_guard
from .llama_index import GovernedQueryEngine, PolicyWorkflowEvent, PolicyWorkflowGuard

__all__ = [
    "GovernedDSPyModule",
    "GovernedDSPyPipeline",
    "GovernedHaystackComponent",
    "make_haystack_policy_guard",
    "GovernedQueryEngine",
    "PolicyWorkflowGuard",
    "PolicyWorkflowEvent",
]
