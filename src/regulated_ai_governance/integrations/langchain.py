"""
LangChain integration — ``FERPAComplianceCallbackHandler`` and
``GovernanceCallbackHandler``.

Provides two LangChain callback handler classes for regulated AI environments:

1. ``FERPAComplianceCallbackHandler``
   Intercepts retrieval results and applies identity-scoped FERPA filtering
   before retrieved documents reach the LLM context window.  Produces a
   ``GovernanceAuditRecord`` for each retrieval event (34 CFR § 99.32).

2. ``GovernanceCallbackHandler``
   Intercepts ``on_tool_start`` events and evaluates each tool invocation
   against an ``ActionPolicy`` before execution proceeds.  This implements
   the "policy-before-execution" principle from ADR-0001: the governance
   check runs synchronously inside the callback so the LangChain chain
   cannot proceed to tool execution without a valid policy decision.
   Produces a ``GovernanceAuditRecord`` for every tool invocation event,
   whether permitted or denied.

Installation:
    pip install regulated-ai-governance[langchain]

Usage — FERPA retrieval filter::

    from regulated_ai_governance.integrations.langchain import (
        FERPAComplianceCallbackHandler,
    )

    audit_log = []
    handler = FERPAComplianceCallbackHandler(
        student_id="stu-alice",
        institution_id="univ-east",
        allowed_categories={"academic_record", "financial_record"},
        audit_sink=audit_log.append,
    )
    retriever = vector_store.as_retriever(callbacks=[handler])
    docs = retriever.invoke("What is my enrollment status?")

Usage — tool-level governance::

    from regulated_ai_governance.integrations.langchain import (
        GovernanceCallbackHandler,
    )
    from regulated_ai_governance.policy import ActionPolicy

    policy = ActionPolicy(allowed_actions={"search_catalog", "read_transcript"})
    gov_handler = GovernanceCallbackHandler(
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=audit_log.append,
    )
    # Pass gov_handler to a LangChain agent or chain via callbacks=[gov_handler]
    # The handler raises PermissionError before any denied tool executes.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from typing import Any

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.documents import Document
except ImportError as exc:
    raise ImportError(
        "langchain-core is required for this integration. "
        "Install it with: pip install regulated-ai-governance[langchain]"
    ) from exc

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy

logger = logging.getLogger(__name__)


class FERPAComplianceCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that enforces FERPA identity boundaries on
    retrieval results before they enter the LLM context window.

    Integrates with LangChain's callback system by intercepting
    ``on_retriever_end`` events. For each retrieval result:

    1. Applies an identity pre-filter (``student_id`` + ``institution_id`` match).
    2. Applies a category authorization filter (if ``allowed_categories`` is set).
    3. Returns only the authorized subset to the chain.
    4. Emits a ``GovernanceAuditRecord`` to the ``audit_sink``.

    **FERPA compliance note:** ``student_id`` and ``institution_id`` must
    originate from the authenticated session token — not from the request body
    or query. The ``audit_sink`` should write to a durable, student-accessible
    store as required by 34 CFR § 99.32.

    :param student_id: Authenticated student identifier from the session.
    :param institution_id: Authenticated institution identifier from the session.
    :param allowed_categories: Optional set of permitted document category values.
        If None, no category filtering is applied (identity check only).
    :param audit_sink: Callable that receives a ``GovernanceAuditRecord`` for
        each retrieval event. Wire to a durable compliance log store.
    :param student_id_field: Metadata field name for the student identifier.
    :param institution_id_field: Metadata field name for the institution identifier.
    :param category_field: Metadata field name for the document category.
    :param raise_on_empty: If True, raise ``PermissionError`` when all documents
        are filtered out. Defaults to False.
    """

    def __init__(
        self,
        student_id: str,
        institution_id: str,
        allowed_categories: set[str] | None = None,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        student_id_field: str = "student_id",
        institution_id_field: str = "institution_id",
        category_field: str = "category",
        raise_on_empty: bool = False,
    ) -> None:
        super().__init__()
        self.student_id = student_id
        self.institution_id = institution_id
        self.allowed_categories = allowed_categories
        self.audit_sink = audit_sink
        self.student_id_field = student_id_field
        self.institution_id_field = institution_id_field
        self.category_field = category_field
        self.raise_on_empty = raise_on_empty

    def _apply_identity_filter(self, documents: list[Document]) -> list[Document]:
        """Layer 1: filter by student_id + institution_id."""
        return [
            doc for doc in documents
            if (
                doc.metadata.get(self.student_id_field) == self.student_id
                and doc.metadata.get(self.institution_id_field) == self.institution_id
            )
        ]

    def _apply_category_filter(self, documents: list[Document]) -> list[Document]:
        """Layer 2: filter by allowed_categories."""
        if not self.allowed_categories:
            return documents
        return [
            doc for doc in documents
            if doc.metadata.get(self.category_field) in self.allowed_categories
        ]

    def on_retriever_end(
        self,
        documents: list[Document],
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> list[Document]:
        """
        Intercept retrieval results and apply FERPA identity filtering.

        Called by the LangChain callback system immediately after a retriever
        returns results. The filtered list is returned to replace the original
        result in the chain.

        :param documents: Raw documents returned by the retriever.
        :param run_id: LangChain run identifier for this retrieval event.
        :param parent_run_id: Parent run identifier.
        :returns: Filtered list of authorized documents.
        :raises PermissionError: If ``raise_on_empty=True`` and all documents
            are filtered out.
        """
        raw_count = len(documents)

        # Two-layer enforcement
        after_identity = self._apply_identity_filter(documents)
        authorized = self._apply_category_filter(after_identity)

        # Emit audit record (34 CFR § 99.32)
        if self.audit_sink is not None:
            record = GovernanceAuditRecord(
                regulation="FERPA",
                actor_id=f"{self.student_id}@{self.institution_id}",
                action_name="retrieval",
                permitted=True,
                context={
                    "documents_in_store": raw_count,
                    "after_identity_filter": len(after_identity),
                    "after_category_filter": len(authorized),
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "student_id": self.student_id,
                    "institution_id": self.institution_id,
                    "allowed_categories": (
                        sorted(self.allowed_categories)
                        if self.allowed_categories
                        else None
                    ),
                },
            )
            self.audit_sink(record)

        if self.raise_on_empty and not authorized:
            raise PermissionError(
                f"FERPAComplianceCallbackHandler: all {raw_count} retrieved documents "
                f"were filtered out for student_id='{self.student_id}' "
                f"institution_id='{self.institution_id}'. "
                "Verify that the document store contains records for this identity."
            )

        return authorized


class GovernanceCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that enforces ``ActionPolicy`` governance on
    every tool invocation before execution proceeds.

    Implements the "policy-before-execution" principle from ADR-0001:
    ``on_tool_start`` is called synchronously by LangChain before the tool
    function runs, so raising ``PermissionError`` here prevents execution.

    For every tool invocation event, a ``GovernanceAuditRecord`` is emitted
    to the ``audit_sink`` whether the action is permitted or denied.

    Regulation citations for common frameworks:
    - FERPA § 99.31(a)(1): access control for school official tools
    - HIPAA § 164.312(a)(1): access controls for PHI-touching tools
    - GLBA § 314.4(c): access controls for customer financial data tools
    - SOC 2 CC6.1: logical access controls for agent-invoked operations

    :param policy: ``ActionPolicy`` defining which tool names are permitted.
        Tool names are matched against ``allowed_actions`` and ``denied_actions``.
    :param regulation: Regulation name written to each ``GovernanceAuditRecord``
        (e.g. ``"FERPA"``, ``"HIPAA"``, ``"GLBA"``).
    :param actor_id: Authenticated principal identifier. Must originate from
        the verified session, not user input.
    :param audit_sink: Optional callable receiving each ``GovernanceAuditRecord``.
        Wire to a durable compliance log store.
    :param tool_name_field: Key in the serialised tool dict whose value is
        used as the action name for policy evaluation. Default: ``"name"``.
    :param block_on_escalation: If ``True`` (default), escalated tools are
        blocked even if the policy would otherwise permit them.
    """

    def __init__(
        self,
        policy: ActionPolicy,
        regulation: str = "FERPA",
        actor_id: str = "unknown",
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        tool_name_field: str = "name",
        block_on_escalation: bool = True,
    ) -> None:
        super().__init__()
        self.regulation = regulation
        self.actor_id = actor_id
        self._audit_sink = audit_sink
        self._guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink,
            block_on_escalation=block_on_escalation,
        )
        self.tool_name_field = tool_name_field

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Intercept tool invocations and evaluate against ``ActionPolicy``.

        Called by the LangChain callback system synchronously before the tool
        function executes.  Raising ``PermissionError`` here prevents execution.

        :param serialized: LangChain serialised tool description dict.  The
            tool name is read from ``serialized[self.tool_name_field]``.
        :param input_str: Raw string input to the tool (for audit context).
        :param run_id: LangChain run identifier for this tool invocation.
        :param parent_run_id: Parent run identifier.
        :raises PermissionError: If the tool name is not permitted by the policy.
        """
        tool_name = serialized.get(self.tool_name_field, "unknown_tool")
        decision = self._guard.evaluate(tool_name)

        # Emit audit record for every tool invocation (permitted or denied)
        if self._audit_sink is not None:
            record = GovernanceAuditRecord(
                regulation=self.regulation,
                actor_id=self.actor_id,
                action_name=tool_name,
                permitted=decision.permitted,
                denial_reason=decision.denial_reason,
                escalation_target=(
                    decision.escalation.escalate_to if decision.escalation else None
                ),
                context={
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "input": input_str,
                },
            )
            self._audit_sink(record)

        if not decision.permitted:
            logger.warning(
                "[GOVERNANCE] Tool blocked: tool=%r actor=%r regulation=%r reason=%r",
                tool_name,
                self.actor_id,
                self.regulation,
                decision.denial_reason,
            )
            raise PermissionError(
                f"GovernanceCallbackHandler: tool '{tool_name}' is not permitted "
                f"for actor '{self.actor_id}' under {self.regulation} policy. "
                f"Reason: {decision.denial_reason}"
            )

        logger.debug(
            "[GOVERNANCE] Tool permitted: tool=%r actor=%r regulation=%r",
            tool_name,
            self.actor_id,
            self.regulation,
        )

    def on_tool_end(self, output: str, *, run_id: uuid.UUID, **kwargs: Any) -> None:
        """No-op: tool end event."""

    def on_tool_error(
        self, error: BaseException | KeyboardInterrupt, *, run_id: uuid.UUID, **kwargs: Any
    ) -> None:
        """No-op: tool error event."""
