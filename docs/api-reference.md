# API Reference — regulated-ai-governance

All public symbols exported from `regulated_ai_governance`.

---

## Core policy primitives

### `ActionPolicy`

Defines which actions an actor is permitted to execute.

```python
@dataclass
class ActionPolicy:
    allowed_actions: set[str]
    denied_actions: set[str] = field(default_factory=set)
    escalation_rules: list[EscalationRule] = field(default_factory=list)
    default_deny: bool = True

    def is_allowed(self, action_name: str) -> PolicyDecision: ...
```

- `allowed_actions` — Set of action name strings the policy permits
- `denied_actions` — Explicitly denied actions (takes precedence over `allowed_actions`)
- `default_deny` — If `True` (default), any action not in `allowed_actions` is denied
- `is_allowed(action_name)` — Returns `PolicyDecision.PERMITTED | DENIED | REQUIRES_HUMAN_REVIEW`

### `EscalationRule`

Marks specific actions as requiring human review rather than outright deny.

```python
@dataclass
class EscalationRule:
    action_pattern: str         # glob or exact match: "read_medical_*"
    reason: str                 # human-readable escalation reason
    escalation_level: str       # "SUPERVISOR" | "COMPLIANCE" | "LEGAL"
```

### `PolicyDecision`

```python
class PolicyDecision(Enum):
    PERMITTED = "PERMITTED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
```

---

## Guard

### `GovernedActionGuard`

Wraps any callable and applies a policy before execution. The wrapped callable only executes if the policy permits.

```python
class GovernedActionGuard:
    def __init__(
        self,
        policy: ActionPolicy,
        regulation: str,
        actor_id: str,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = False,
    ): ...

    def guard(
        self,
        action_name: str,
        execute_fn: Callable[[], Any],
        context: dict | None = None,
    ) -> Any: ...
```

**Parameters:**
- `policy` — The `ActionPolicy` to evaluate
- `regulation` — Regulation name for audit records (e.g., `"FERPA"`, `"HIPAA"`)
- `actor_id` — ID of the agent or user performing the action
- `audit_sink` — Callback invoked with every `GovernanceAuditRecord` (permitted or denied)
- `block_on_escalation` — If `True`, `REQUIRES_HUMAN_REVIEW` blocks execution; if `False`, it executes but logs

**`guard(action_name, execute_fn)`** — Evaluates the policy and either:
- Returns `execute_fn()` result if permitted
- Raises `PolicyViolationError` if denied
- Returns result or raises (depending on `block_on_escalation`) if `REQUIRES_HUMAN_REVIEW`

The `audit_sink` is always called, regardless of outcome.

---

## Orchestrator (multi-framework)

### `GovernanceOrchestrator`

Applies multiple `GovernedActionGuard` instances simultaneously with deny-all aggregation: any single denial causes overall denial.

```python
class GovernanceOrchestrator:
    def __init__(
        self,
        framework_guards: list[FrameworkGuard],
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
    ): ...

    def guard(
        self,
        action_name: str,
        execute_fn: Callable[[], Any],
        actor_id: str,
        context: dict | None = None,
    ) -> Any: ...

    @property
    def last_report(self) -> ComprehensiveAuditReport: ...
```

### `FrameworkGuard`

Named wrapper for a `GovernedActionGuard` in the orchestrator.

```python
@dataclass
class FrameworkGuard:
    framework_name: str
    guard: GovernedActionGuard
```

### `ComprehensiveAuditReport`

Report produced by the orchestrator after every evaluation.

```python
@dataclass
class ComprehensiveAuditReport:
    framework_results: list[FrameworkResult]
    overall_decision: MultiFrameworkDecision
    is_compliant: bool

    def to_compliance_summary(self) -> str: ...
    def to_dict(self) -> dict: ...

class MultiFrameworkDecision(Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    PARTIALLY_APPROVED = "PARTIALLY_APPROVED"
```

---

## Audit record

### `GovernanceAuditRecord`

Structured compliance audit record produced by every guard evaluation.

```python
@dataclass
class GovernanceAuditRecord:
    filter_name: str
    decision: str                  # "PERMITTED" | "DENIED" | "REQUIRES_HUMAN_REVIEW"
    reason: str
    regulation_citation: str       # e.g., "34 CFR §99.31(a)(1) — FERPA 1974"
    requires_logging: bool
    actor_id: str
    action_name: str
    timestamp: str                 # ISO 8601

    def to_log_entry(self) -> str: ...
    def to_dict(self) -> dict: ...
```

JSON-serializable; sink to PostgreSQL, BigQuery, Splunk, or any SIEM.

---

## High-level skill API

### `GovernanceAuditSkill`

High-level factory API. Wraps `GovernanceOrchestrator` with pre-configured regulation sets.

```python
class GovernanceAuditSkill:
    @classmethod
    def for_education(
        cls,
        actor_id: str,
        audit_sink: Callable | None = None,
    ) -> "GovernanceAuditSkill": ...

    @classmethod
    def for_healthcare(
        cls,
        actor_id: str,
        audit_sink: Callable | None = None,
    ) -> "GovernanceAuditSkill": ...

    @classmethod
    def for_financial(
        cls,
        actor_id: str,
        audit_sink: Callable | None = None,
    ) -> "GovernanceAuditSkill": ...

    @classmethod
    def for_government(
        cls,
        actor_id: str,
        audit_sink: Callable | None = None,
    ) -> "GovernanceAuditSkill": ...

    def audit_action(
        self,
        action_name: str,
        execute_fn: Callable[[], Any],
    ) -> Any: ...

    def audit_retrieval(
        self,
        documents: list[dict],
        actor_id: str,
    ) -> tuple[list[dict], ComprehensiveAuditReport]: ...
```

Pre-configured regulation sets:
- `for_education()` → FERPA + OWASP LLM Top 10
- `for_healthcare()` → HIPAA + FDA AI/ML Action Plan
- `for_financial()` → GLBA + FINRA + SEC Reg S-P
- `for_government()` → FedRAMP + FISMA + CUI

---

## Regulation factories

Each regulation module provides a `make_*_policy()` factory:

```python
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy
from regulated_ai_governance.regulations.hipaa import make_hipaa_covered_entity_policy
from regulated_ai_governance.regulations.gdpr import make_gdpr_data_processor_policy
from regulated_ai_governance.regulations.glba import make_glba_financial_institution_policy
```

All factories return an `ActionPolicy` pre-configured for the regulation.

---

## Framework adapters

### CrewAI — `regulated_ai_governance.integrations.crewai`

```python
from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard

guard = EnterpriseActionGuard(
    wrapped_tool=MyTool(),
    policy=policy,
    regulation="FERPA",
    actor_id="agent-advisor",
    audit_sink=lambda rec: write_to_db(rec),
    block_on_escalation=True,
)
agent = Agent(tools=[guard], ...)
```

`EnterpriseActionGuard` is a drop-in replacement for any CrewAI tool.

### LangChain — `regulated_ai_governance.integrations.langchain`

```python
from regulated_ai_governance.integrations.langchain import GovernanceCallbackHandler

handler = GovernanceCallbackHandler(
    regulations=["FERPA", "HIPAA"],
    actor_id="advisor_007",
    audit_sink=lambda rec: my_siem.ingest(rec),
)
llm = ChatOpenAI(callbacks=[handler])
```

### Google ADK — `regulated_ai_governance.adapters.google_adk_adapter`

```python
from regulated_ai_governance.adapters.google_adk_adapter import (
    ADKPolicyGuard, Regulation, BigQueryAuditSink
)

class Regulation(Enum):
    FERPA = "FERPA"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    GLBA = "GLBA"
    EU_AI_ACT = "EU_AI_ACT"
    OWASP_AGENTIC = "OWASP_AGENTIC"

guard = ADKPolicyGuard(
    regulations=[Regulation.FERPA, Regulation.HIPAA],
    audit_sink=BigQueryAuditSink(project="my-gcp-project", dataset="ai_audit"),
    agent_id="student-advisor",
    authorized_roles=["academic_advisor"],
    authorized_data_categories=["academic_record", "financial_aid"],
)
```

`ADKPolicyGuard` implements `before_model_callback`, `before_agent_callback`, and `before_tool_callback` — assign any or all to an ADK `LlmAgent`.

### LlamaIndex — `regulated_ai_governance.integrations.llama_index`

```python
from regulated_ai_governance.integrations.llama_index import ComplianceNodePostprocessor

postprocessor = ComplianceNodePostprocessor(policy=policy, actor_id="advisor_007")
```

---

## Base filter primitives

For building custom regulation modules:

```python
from regulated_ai_governance.base import GovernanceFilter, FilterResult, GovernancePipeline

class MyCustomFilter(GovernanceFilter):
    def evaluate(self, context: Any, document: dict) -> FilterResult:
        # Return FilterResult.permit() or FilterResult.deny("reason")
        ...
```

`GovernancePipeline` chains multiple `GovernanceFilter` instances with deny-all aggregation.
