"""
integrations — Framework integration adapters for regulated AI governance.

Provides policy-enforcement bridge components for popular agentic AI frameworks.
All framework-specific imports are lazy so the package is importable without
any framework dependency installed.

Integration modules (import from the named submodule unless exported below)
-------------------------------------------------------------------------
- ``crewai.EnterpriseActionGuard`` — legacy wrapper; native SDK quarantined
- ``autogen.GovernedAutoGenAgent`` — legacy object wrapper; SDK extra quarantined
- ``dspy.GovernedDSPyModule`` / ``GovernedDSPyPipeline`` — no qualified native SDK extra
- ``semantic_kernel.GovernedKernelPlugin`` — SK integration
- ``maf.PolicyMiddleware`` — MAF middleware with ``as_native()`` bridge
- ``langchain.GovernanceCallbackHandler`` / ``FERPAComplianceCallbackHandler``
- ``haystack.GovernedHaystackComponent`` / ``make_haystack_policy_guard``
- ``llama_index.GovernedQueryEngine`` / ``PolicyWorkflowGuard`` / ``PolicyWorkflowEvent``

See ECOSYSTEM.md, SECURITY.md and package metadata for current version/Python
boundaries. Source availability does not establish native SDK qualification.
The separate ``adapters.semantic_kernel.PolicyKernelPlugin`` is not this
package's ``integrations.semantic_kernel.GovernedKernelPlugin``.
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
