"""
integrations — Framework integration adapters for regulated AI governance.

Provides policy-enforcement bridge components for popular agentic AI frameworks.
All framework-specific imports are lazy so the package is importable without
any framework dependency installed.

Available integrations
----------------------
- ``EnterpriseActionGuard``   — CrewAI ``BaseTool`` wrapper (crewai>=1.14)
- ``PolicyEnforcingAgent``    — AutoGen agent with inline policy enforcement
- ``PolicyKernelPlugin``      — Semantic Kernel function plugin
- ``PolicyMiddleware``        — Microsoft Agent Framework (MAF) middleware (NEW — MAF 2026)
- ``LangChainPolicyGuard``    — LangChain tool wrapper
- ``LlamaIndexPolicyFilter``  — LlamaIndex node postprocessor
- ``HaystackPolicyGuard``     — Haystack 2.x pipeline component

Note on AutoGen and Semantic Kernel:
Both AutoGen and Semantic Kernel are in maintenance mode as of 2026. Microsoft
recommends migrating to Microsoft Agent Framework (MAF). The AutoGen and
Semantic Kernel integrations remain available for backward compatibility, but
new projects should use the MAF integration (``PolicyMiddleware``).
"""
