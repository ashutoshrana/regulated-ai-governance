# Implementation Note 03 — Adapter Pattern for Multi-Framework Integrations

**Repo:** `regulated-ai-governance`
**Relates to:** [`examples/02_crewai_guard.py`](../examples/02_crewai_guard.py), [`examples/03_multi_framework_orchestration.py`](../examples/03_multi_framework_orchestration.py)
**ADR cross-reference:** [ADR-003 (adapter-over-inheritance)](adr/003-adapter-over-inheritance.md), [ADR-004 (framework-agnostic-core)](adr/004-framework-agnostic-core.md)

---

## The problem: tight coupling between compliance logic and agent frameworks

AI agent frameworks (CrewAI, AutoGen, LangChain, Semantic Kernel, Haystack, DSPy, Microsoft Agent Framework) each have their own tool/function invocation lifecycle. If compliance logic is written against one framework's API, it cannot be reused across others without a rewrite.

This is a non-trivial risk for EB-1A-quality evidence, but more immediately for production systems: organizations running multiple frameworks (a common pattern when different teams adopt different frameworks for different use cases) end up with duplicated compliance logic that diverges over time. When a regulation changes, the team must update N implementations instead of one.

The adapter pattern solves this by separating:
- **Compliance core** — `GovernedActionGuard`, `ActionPolicy`, `EscalationRule`, `GovernanceOrchestrator` — framework-agnostic, tested independently
- **Framework adapters** — thin wrappers that translate each framework's invocation lifecycle into the core's `guard(action_name, execute_fn)` interface

Adding a new framework requires writing one adapter class. The compliance core does not change.

---

## The adapter interface

Each framework adapter implements the same conceptual contract:

```
FrameworkAdapter
  wrap_tool(tool, guard) → framework-native tool or function
  wrap_pipeline(pipeline, orchestrator) → governed pipeline
```

The adapter intercepts the framework's tool invocation, extracts the action name (usually the function/tool name), and calls `guard.guard(action_name, execute_fn=lambda: original_tool(**kwargs))`.

The result is returned to the framework as if the original tool had been called directly. If the governance layer denies the action, the adapter raises the framework's expected exception type — `PermissionError` for most, but `ToolException` for LangChain, `BlockedMessageException` for AutoGen, etc.

This exception mapping is the only framework-specific logic in an adapter.

---

## Existing adapters and their integration points

| Module | Framework | Integration point |
|--------|-----------|------------------|
| `integrations/crewai.py` | CrewAI 1.x | Wraps `BaseTool` subclasses; `EnterpriseActionGuard` is itself a `BaseTool` |
| `integrations/langchain.py` | LangChain Community | `FERPAComplianceCallbackHandler` hooks `on_retriever_start/end` |
| `integrations/autogen.py` | AutoGen 0.4+ / MAF | `GovernedFunctionTool` wraps the function tool registration |
| `integrations/semantic_kernel.py` | SK 1.x | `GovernedKernelPlugin` wraps kernel function invocation |
| `integrations/haystack.py` | Haystack 2.x | `GovernedRetrieverWrapper` wraps `run()` on any retriever |
| `integrations/llama_index.py` | LlamaIndex 0.10+ | `GovernedQueryEngineTool` wraps `QueryEngine.query()` |
| `integrations/dspy.py` | DSPy 2.x | `GovernedDSPyModule` wraps `forward()` on any Module |
| `integrations/maf.py` | Microsoft Agent Framework | `GovernedMAFAgent` wraps agent message handling |
| `adapters/crewai.py` | CrewAI (legacy) | Original CrewAI adapter (maintained for backward compat) |
| `adapters/autogen.py` | AutoGen 0.2.x | Legacy AutoGen adapter |

---

## Writing a new adapter: step-by-step

The following pattern applies to any new framework. This example adds a hypothetical `smolagents` (HuggingFace small agents) adapter.

### Step 1 — Understand the framework's tool invocation lifecycle

```python
# smolagents tool invocation example
class MyTool(Tool):
    name = "search_database"
    
    def forward(self, query: str) -> str:
        return db.search(query)
```

The interception point is `forward()`.

### Step 2 — Create the adapter module

```python
# src/regulated_ai_governance/integrations/smolagents.py
from __future__ import annotations
from typing import Any, Callable
from regulated_ai_governance.agent_guard import GovernedActionGuard


class GovernedSmolagentsTool:
    """
    Wraps a smolagents ``Tool`` to enforce governance before ``forward()`` is called.
    """

    def __init__(self, tool: Any, guard: GovernedActionGuard) -> None:
        self._tool = tool
        self._guard = guard

    def forward(self, **kwargs: Any) -> Any:
        action_name: str = getattr(self._tool, "name", type(self._tool).__name__)

        def execute() -> Any:
            return self._tool.forward(**kwargs)

        result = self._guard.guard(action_name=action_name, execute_fn=execute)
        return result.execute_result
```

### Step 3 — Map framework exceptions

If the framework expects a specific exception type on denial, add a try/except:

```python
try:
    result = self._guard.guard(action_name=action_name, execute_fn=execute)
except PermissionError as exc:
    raise SmolagentsToolDeniedException(str(exc)) from exc
```

### Step 4 — Add a `__init__.py` export and a test

```python
# In src/regulated_ai_governance/integrations/__init__.py
from regulated_ai_governance.integrations.smolagents import GovernedSmolagentsTool

# In tests/test_integrations.py
def test_smolagents_adapter_blocks_denied_action():
    ...
```

### Step 5 — Update ECOSYSTEM.md and README

Add the new framework to the integration matrix. No changes to the compliance core are needed.

---

## Testing strategy: guards in isolation vs. end-to-end

**Unit testing guards (preferred):** Test `GovernedActionGuard` with a manually constructed `ActionPolicy`. This is fast, has no external dependencies, and covers all policy branches.

```python
def test_hipaa_guard_denies_external_disclosure():
    policy = ActionPolicy(
        allowed_actions={"read_vitals"},
        denied_actions={"share_phi_externally"},
    )
    guard = GovernedActionGuard(policy=policy, regulation="HIPAA", actor_id="nurse_1")
    result = guard.evaluate("share_phi_externally")
    assert not result.permitted
    assert "explicitly denied" in result.denial_reason
```

**Integration testing adapters:** Test the adapter with a mock framework tool. Verify that:
1. A permitted action passes through and returns the original tool's result
2. A denied action raises the framework-expected exception
3. The `audit_sink` receives a `GovernanceAuditRecord` in both cases

```python
def test_crewai_adapter_passes_through_permitted_action():
    mock_tool = MockCRMTool()
    guard = GovernedActionGuard(
        policy=ActionPolicy(allowed_actions={"read_account"}),
        regulation="ISO27001",
        actor_id="agent_1",
    )
    governed = EnterpriseActionGuard(tool=mock_tool, guard=guard)
    result = governed._run("read_account", {"account_id": "acc_001"})
    assert result == mock_tool.expected_output
```

**End-to-end testing with real frameworks:** Reserve for CI pipelines where the framework is installed. Use `pytest.importorskip("crewai")` to skip if the optional dependency is absent.

---

## Versioning adapters independently of the core

Framework APIs change frequently. CrewAI 1.0 broke compatibility with 0.x. AutoGen 0.4 (now Microsoft Agent Framework) is API-incompatible with 0.2.

Adapters are versioned independently of the governance core by encoding the framework version in the module path convention. When a major framework version introduces breaking changes:

1. Create a new adapter module (`integrations/crewai_v2.py`)
2. Deprecate the old one with a `DeprecationWarning` in `__init__`
3. Maintain the old adapter for one major release cycle

The governance core (`agent_guard.py`, `orchestrator.py`, `policy.py`) has no dependency on any framework and therefore never needs a version-conditional code path. Framework version complexity lives entirely in adapters.
