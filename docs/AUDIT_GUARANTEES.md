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
