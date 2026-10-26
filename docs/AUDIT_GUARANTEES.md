# Audit guarantees

`GovernanceAuditRecord` is a frozen snapshot of finite JSON-compatible context.
Nested mappings and sequences cannot be changed through the record. Exported
log dictionaries are independent copies. This does not make storage tamper-proof.
Store only approved, redacted metadata; the record does not automatically redact.

```python
from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.policy import ActionPolicy

records = []  # Demonstration only: use a durable, acknowledged sink in production.
guard = GovernedActionGuard(
    ActionPolicy(allowed_actions={"update_case"}),
    actor_id="authenticated-principal",
    audit_sink=records.append,
    require_audit=True,
    audit_execution=True,
    raise_on_deny=True,
)
guard.guard("update_case", lambda: "updated", {"workflow_id": "synthetic-001"})
assert [r.event_type for r in records] == ["decision", "execution"]
assert records[0].correlation_id == records[1].correlation_id
```

- `require_audit=True` rejects construction without a sink. Any configured sink
  must acknowledge the decision before the action is invoked; exceptions stop it.
  Async sinks and awaitable return values are rejected; dispatching a background
  task does not constitute acknowledged durable delivery.
- `audit_execution=True` adds succeeded/failed events for synchronous callables.
  It requires a sink and rejects async callables/results; it cannot audit awaited
  completion. Existing response-only behavior remains available by default.
- A denied action emits a decision, never an execution event.
- `AuditDeliveryError.action_executed=False` means the action was not invoked.
  `True` means it was invoked and may have produced side effects. Do not blindly
  retry; reconcile by application idempotency key. A post-action audit failure
  cannot roll back external systems. Sink exceptions remain chained as causes.
- Direct `evaluate()` is a policy preview, not execution and not an audit write.
- Decision and outcome reuse the same pre-action context snapshot, even when the
  action mutates its caller's context.
- Sink durability, retention, authentication, and access restrictions belong to
  the application. A list or ordinary file append is not an acknowledged remote
  compliance store.

Migration: audit contexts must contain finite JSON values with string keys.
Serialize custom objects and redact sensitive values before creating a record.
Use a new record for a correction rather than mutating historical data.

Check: `pytest -q tests/test_audit_guarantees.py`.

Integration factories accept `require_audit=True` and pass it to the shared
action guard. Missing sinks reject construction; configured sinks must
acknowledge delivery synchronously before guarded actions execute. These
adapters emit decision records; they do not claim awaited execution outcomes.

LangChain `GovernanceCallbackHandler` checks tools and the `retrieval` action
in start callbacks with propagated exceptions. Attach it to the actual
invocation. `FERPAComplianceCallbackHandler` filters the native result list in
place because callback return values are ignored. That filter runs after the
retrieval read; use the governance start handler to block retrieval itself. An
empty allowed-category set permits no category. The skill's LangChain handler
uses its existing `document_retrieval` action and configured framework rules.

For LlamaIndex protect the query engine with `GovernedQueryEngine.wrap(...)`.
For Haystack protect the whole pipeline through
`GovernedHaystackComponent.guard_callable(pipeline.run, ...)` before retrieval.
A guard inserted after a retriever only controls downstream document use; it
cannot prevent a read that already happened. Likewise `PolicyWorkflowGuard`
checks its received event, after any earlier workflow steps.

`GovernanceAuditSkill` convenience factories delegate the same configured
frameworks and audit sink as `audit_action` and `audit_retrieval`:

- `as_crewai_tool` returns a native tool with the callable's input signature and
  checks its configured action before invoking the callable.
- `as_llama_index_postprocessor` and `as_haystack_component` return native SDK
  objects that apply `document_retrieval` rules to already retrieved content.
  Denial returns an empty collection; these do not prevent the earlier read or
  independently verify document identity.
- `as_maf_middleware` returns native Microsoft `FunctionMiddleware` for
  `Agent(..., middleware=[...])`; it checks `context.function.name` before
  calling the next middleware. It does not intercept model calls or arbitrary
  agent messages. Install the `maf` extra (`agent-framework-core`, Python 3.10+).
  The concrete `integrations.maf.PolicyMiddleware` keeps its legacy `on_message`
  interface; register `policy_middleware.as_native()` to use its existing action
  policy through native function middleware.

The skill's existing `audit_only=True` intentionally permits actions and content
while recording denials. Configured synchronous sink failures propagate before
tool calls or downstream content delivery; async sink delivery is not supported
by these skill convenience adapters. No adapter establishes legal compliance.
Native factory tests live in `tests/test_skill.py::test_native_skill_factory`.

Native regression checks: `tests/test_native_langchain_boundary.py` and
`tests/test_native_retrieval_wrappers.py`; SDK installation is required.
