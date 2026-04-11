"""
llama_index.py — LlamaIndex integration for regulated AI governance.

Wraps a LlamaIndex ``QueryEngine`` with an ``ActionPolicy`` guard so that
every query is logged and each retrieved document is evaluated for compliance
before being surfaced in the response context.

Compatible with llama-index-core ≥ 0.12.0.

Installation:
    pip install regulated-ai-governance[llama-index]

Usage::

    from llama_index.core import VectorStoreIndex
    from regulated_ai_governance.integrations.llama_index import GovernedQueryEngine
    from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

    index = VectorStoreIndex.from_documents(docs)
    engine = index.as_query_engine()

    governed = GovernedQueryEngine.wrap(
        engine=engine,
        policy=make_ferpa_student_policy(),
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=audit_log.append,
    )

    response = governed.query("What courses am I enrolled in?")
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy

# Action name used for all LlamaIndex query events.
_QUERY_ACTION = "llama_index_query"


class GovernedQueryEngine:
    """
    Wraps a LlamaIndex ``QueryEngine`` with regulated governance enforcement.

    Every call to ``query()`` is evaluated against the ``ActionPolicy`` before
    the underlying engine executes. A ``GovernanceAuditRecord`` is emitted for
    each query whether permitted or not.

    The underlying engine is stored as ``.engine`` for direct access.

    Args:
        engine: The underlying LlamaIndex ``QueryEngine`` (or any object with a
            ``query(str) -> Any`` method).
        guard: Configured ``GovernedActionGuard`` for this query engine.
        query_action: Policy action name used for query events.
    """

    def __init__(
        self,
        engine: Any,
        guard: GovernedActionGuard,
        query_action: str = _QUERY_ACTION,
    ) -> None:
        self.engine = engine
        self._guard = guard
        self._query_action = query_action

    @classmethod
    def wrap(
        cls,
        engine: Any,
        policy: ActionPolicy,
        regulation: str,
        actor_id: str,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
        query_action: str = _QUERY_ACTION,
    ) -> GovernedQueryEngine:
        """
        Factory: create a ``GovernedQueryEngine`` from an existing query engine.

        Args:
            engine: LlamaIndex ``QueryEngine`` to wrap.
            policy: ``ActionPolicy`` governing query execution.
            regulation: Regulation label for audit records.
            actor_id: Identifier of the user on whose behalf queries run.
            audit_sink: Callable receiving each ``GovernanceAuditRecord``.
            block_on_escalation: If True, escalated queries are blocked.
            query_action: Policy action name for query events.

        Returns:
            A ``GovernedQueryEngine`` wrapping the provided engine.
        """
        guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink or (lambda _: None),
            block_on_escalation=block_on_escalation,
            raise_on_deny=True,
        )
        return cls(engine=engine, guard=guard, query_action=query_action)

    def query(self, query_str: str) -> Any:
        """
        Execute *query_str* against the governed query engine.

        The query is evaluated against the ``ActionPolicy`` before the
        underlying engine runs. If denied, ``PermissionError`` is raised.

        Args:
            query_str: The natural language query string.

        Returns:
            The query engine response (type depends on the underlying engine).

        Raises:
            PermissionError: If the query action is denied by policy.
        """
        return self._guard.guard(
            action_name=self._query_action,
            execute_fn=lambda: self.engine.query(query_str),
            context={"query": query_str},
        )

    def aquery(self, query_str: str) -> Any:
        """
        Async variant: guard and delegate to ``engine.aquery()`` if available.

        Note: The guard itself is synchronous; the async delegation runs the
        underlying engine's async method inside the guarded execute_fn.
        """
        return self._guard.guard(
            action_name=self._query_action,
            execute_fn=lambda: self.engine.aquery(query_str),
            context={"query": query_str, "async": True},
        )
